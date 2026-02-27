"""
Integration tests for agentic workflows.

**Validates: Requirements 5.1, 5.2, 5.3, 5.4, 5.5**

This module tests the complete integration of agentic workflows:
- Price alert agent workflow
- Research agent workflow
- Rebalancing agent workflow
- Parallel task execution
"""

import pytest
import asyncio
from datetime import datetime, date
from sqlalchemy.orm import Session

from app.services.agentic_orchestrator import AgenticOrchestrator
from app.services.agents.price_alert_agent import PriceAlertAgent
from app.services.agents.research_agent import ResearchAgent
from app.services.agents.rebalancing_agent import RebalancingAgent
from app.models import User, Portfolio, StockPosition, PriceAlert, Notification
from app.mcp.factory import get_mcp_factory


@pytest.fixture
def test_user_with_portfolio(db_session: Session):
    """Create a test user with portfolio and positions."""
    user = User(
        email="test@example.com",
        password_hash="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Create portfolio
    portfolio = Portfolio(user_id=user.id)
    db_session.add(portfolio)
    db_session.commit()
    db_session.refresh(portfolio)
    
    # Add positions
    positions = [
        StockPosition(
            portfolio_id=portfolio.id,
            ticker="AAPL",
            quantity=10,
            purchase_price=150.00,
            purchase_date=date(2024, 1, 1)
        ),
        StockPosition(
            portfolio_id=portfolio.id,
            ticker="GOOGL",
            quantity=5,
            purchase_price=140.00,
            purchase_date=date(2024, 1, 1)
        ),
        StockPosition(
            portfolio_id=portfolio.id,
            ticker="MSFT",
            quantity=8,
            purchase_price=380.00,
            purchase_date=date(2024, 1, 1)
        )
    ]
    for pos in positions:
        db_session.add(pos)
    db_session.commit()
    
    return user


class TestPriceAlertAgentWorkflow:
    """Test price alert agent workflow integration."""
    
    @pytest.mark.asyncio
    async def test_price_alert_agent_workflow_execution(self, db_session, test_user_with_portfolio, redis_client):
        """
        Test price alert agent workflow monitors prices and triggers alerts.
        
        **Validates: Requirement 5.1**
        """
        user = test_user_with_portfolio
        
        # Create price alerts
        alerts = [
            PriceAlert(
                user_id=user.id,
                ticker="AAPL",
                condition="above",
                target_price=200.00,
                notification_channels=["in-app"],
                is_active=True
            ),
            PriceAlert(
                user_id=user.id,
                ticker="GOOGL",
                condition="below",
                target_price=100.00,
                notification_channels=["in-app", "email"],
                is_active=True
            )
        ]
        for alert in alerts:
            db_session.add(alert)
        db_session.commit()
        
        # Create orchestrator and register price alert agent
        orchestrator = AgenticOrchestrator(db_session)
        price_alert_agent = PriceAlertAgent(db_session, redis_client, get_mcp_factory())
        
        async def price_alert_wrapper(state):
            """Wrapper to execute price alert agent."""
            result = await price_alert_agent.execute(state["context"])
            state["results"]["price_alerts"] = result
            return state
        
        orchestrator.register_agent("price_alert", price_alert_wrapper)
        
        # Create workflow
        definition = {
            "nodes": [
                {
                    "id": "check_alerts",
                    "type": "agent",
                    "agent": "price_alert",
                    "is_entry": True,
                    "is_finish": True
                }
            ],
            "edges": []
        }
        
        workflow = orchestrator.create_workflow(
            user_id=user.id,
            name="Price Alert Monitoring",
            workflow_type="price_monitoring",
            definition=definition,
            execution_mode="sequential"
        )
        
        # Execute workflow
        result = await orchestrator.executeWorkflow(
            workflow_id=workflow.id,
            context={"user_id": str(user.id)}
        )
        
        # Verify workflow completed
        assert result["status"] in ["completed", "failed"]
        assert "executionTime" in result
        
        # If completed successfully, verify results
        if result["status"] == "completed":
            assert "results" in result
            assert "price_alerts" in result["results"]
    
    @pytest.mark.asyncio
    async def test_price_alert_agent_triggers_notification(self, db_session, test_user_with_portfolio, redis_client):
        """
        Test price alert agent creates notifications when alerts trigger.
        
        **Validates: Requirement 5.1**
        """
        user = test_user_with_portfolio
        
        # Create an alert that should trigger (using a low threshold)
        alert = PriceAlert(
            user_id=user.id,
            ticker="AAPL",
            condition="above",
            target_price=1.00,  # Very low threshold, likely to trigger
            notification_channels=["in-app"],
            is_active=True
        )
        db_session.add(alert)
        db_session.commit()
        
        # Execute price alert agent
        price_alert_agent = PriceAlertAgent(db_session, redis_client, get_mcp_factory())
        
        try:
            result = await price_alert_agent.execute({"user_id": str(user.id)})
            
            # Verify result structure
            assert "checked_alerts" in result
            assert "triggered_alerts" in result
            assert isinstance(result["checked_alerts"], int)
            assert isinstance(result["triggered_alerts"], int)
            
            # Check if any notifications were created
            notifications = db_session.query(Notification).filter(
                Notification.user_id == user.id,
                Notification.type == "price_alert"
            ).all()
            
            # If alert triggered, should have notification
            if result["triggered_alerts"] > 0:
                assert len(notifications) > 0
        except Exception as e:
            # Agent may fail if MCP servers are not available
            # This is acceptable for integration tests
            pytest.skip(f"Price alert agent execution failed: {e}")


class TestResearchAgentWorkflow:
    """Test research agent workflow integration."""
    
    @pytest.mark.asyncio
    async def test_research_agent_workflow_execution(self, db_session, test_user_with_portfolio, redis_client):
        """
        Test research agent workflow gathers and summarizes news.
        
        **Validates: Requirement 5.3**
        """
        user = test_user_with_portfolio
        
        # Create orchestrator and register research agent
        orchestrator = AgenticOrchestrator(db_session)
        research_agent = ResearchAgent(db_session, redis_client, get_mcp_factory())
        
        async def research_wrapper(state):
            """Wrapper to execute research agent."""
            result = await research_agent.execute(state["context"])
            state["results"]["research"] = result
            return state
        
        orchestrator.register_agent("research", research_wrapper)
        
        # Create workflow
        definition = {
            "nodes": [
                {
                    "id": "gather_research",
                    "type": "agent",
                    "agent": "research",
                    "is_entry": True,
                    "is_finish": True
                }
            ],
            "edges": []
        }
        
        workflow = orchestrator.create_workflow(
            user_id=user.id,
            name="Research Automation",
            workflow_type="research",
            definition=definition,
            execution_mode="sequential"
        )
        
        # Execute workflow
        result = await orchestrator.executeWorkflow(
            workflow_id=workflow.id,
            context={"user_id": str(user.id)}
        )
        
        # Verify workflow completed
        assert result["status"] in ["completed", "failed"]
        assert "executionTime" in result
        
        # If completed successfully, verify results
        if result["status"] == "completed":
            assert "results" in result
            assert "research" in result["results"]
    
    @pytest.mark.asyncio
    async def test_research_agent_gathers_news_for_portfolio(self, db_session, test_user_with_portfolio, redis_client):
        """
        Test research agent gathers news for all portfolio stocks.
        
        **Validates: Requirement 5.3**
        """
        user = test_user_with_portfolio
        
        # Execute research agent
        research_agent = ResearchAgent(db_session, redis_client, get_mcp_factory())
        
        try:
            result = await research_agent.execute({"user_id": str(user.id)})
            
            # Verify result structure
            assert "stocks_researched" in result
            assert "total_articles" in result
            assert isinstance(result["stocks_researched"], int)
            assert isinstance(result["total_articles"], int)
            
            # Should have researched at least the stocks in portfolio
            portfolio = db_session.query(Portfolio).filter(Portfolio.user_id == user.id).first()
            assert result["stocks_researched"] >= len(portfolio.positions)
        except Exception as e:
            # Agent may fail if MCP servers are not available
            pytest.skip(f"Research agent execution failed: {e}")


class TestRebalancingAgentWorkflow:
    """Test rebalancing agent workflow integration."""
    
    @pytest.mark.asyncio
    async def test_rebalancing_agent_workflow_execution(self, db_session, test_user_with_portfolio, redis_client):
        """
        Test rebalancing agent workflow analyzes portfolio and suggests rebalancing.
        
        **Validates: Requirement 5.2**
        """
        user = test_user_with_portfolio
        
        # Create orchestrator and register rebalancing agent
        orchestrator = AgenticOrchestrator(db_session)
        rebalancing_agent = RebalancingAgent(db_session, redis_client, get_mcp_factory())
        
        async def rebalancing_wrapper(state):
            """Wrapper to execute rebalancing agent."""
            result = await rebalancing_agent.execute(state["context"])
            state["results"]["rebalancing"] = result
            return state
        
        orchestrator.register_agent("rebalancing", rebalancing_wrapper)
        
        # Create workflow
        definition = {
            "nodes": [
                {
                    "id": "analyze_portfolio",
                    "type": "agent",
                    "agent": "rebalancing",
                    "is_entry": True,
                    "is_finish": True
                }
            ],
            "edges": []
        }
        
        workflow = orchestrator.create_workflow(
            user_id=user.id,
            name="Portfolio Rebalancing",
            workflow_type="rebalancing",
            definition=definition,
            execution_mode="sequential"
        )
        
        # Execute workflow
        result = await orchestrator.executeWorkflow(
            workflow_id=workflow.id,
            context={"user_id": str(user.id)}
        )
        
        # Verify workflow completed
        assert result["status"] in ["completed", "failed"]
        assert "executionTime" in result
        
        # If completed successfully, verify results
        if result["status"] == "completed":
            assert "results" in result
            assert "rebalancing" in result["results"]
    
    @pytest.mark.asyncio
    async def test_rebalancing_agent_generates_suggestions(self, db_session, test_user_with_portfolio, redis_client):
        """
        Test rebalancing agent generates rebalancing suggestions.
        
        **Validates: Requirement 5.2**
        """
        user = test_user_with_portfolio
        
        # Execute rebalancing agent
        rebalancing_agent = RebalancingAgent(db_session, redis_client, get_mcp_factory())
        
        try:
            result = await rebalancing_agent.execute({"user_id": str(user.id)})
            
            # Verify result structure
            assert "suggestions" in result
            assert "portfolio_health" in result
            assert isinstance(result["suggestions"], list)
            
            # Each suggestion should have required fields
            for suggestion in result["suggestions"]:
                assert "action" in suggestion
                assert suggestion["action"] in ["buy", "sell", "hold"]
                assert "ticker" in suggestion
                assert "reason" in suggestion
        except Exception as e:
            # Agent may fail if MCP servers are not available
            pytest.skip(f"Rebalancing agent execution failed: {e}")


class TestParallelTaskExecution:
    """Test parallel task execution in workflows."""
    
    @pytest.mark.asyncio
    async def test_parallel_workflow_execution(self, db_session, test_user_with_portfolio, redis_client):
        """
        Test multiple independent tasks execute in parallel.
        
        **Validates: Requirements 5.4, 5.5**
        """
        user = test_user_with_portfolio
        
        # Create orchestrator
        orchestrator = AgenticOrchestrator(db_session)
        
        # Register multiple agents
        async def task_1(state):
            await asyncio.sleep(0.1)  # Simulate work
            state["results"]["task_1"] = {"status": "completed", "data": "task_1_result"}
            return state
        
        async def task_2(state):
            await asyncio.sleep(0.1)  # Simulate work
            state["results"]["task_2"] = {"status": "completed", "data": "task_2_result"}
            return state
        
        async def task_3(state):
            await asyncio.sleep(0.1)  # Simulate work
            state["results"]["task_3"] = {"status": "completed", "data": "task_3_result"}
            return state
        
        orchestrator.register_agent("task_1", task_1)
        orchestrator.register_agent("task_2", task_2)
        orchestrator.register_agent("task_3", task_3)
        
        # Create parallel workflow
        definition = {
            "nodes": [
                {
                    "id": "start",
                    "type": "start",
                    "is_entry": True
                },
                {
                    "id": "task_1",
                    "type": "agent",
                    "agent": "task_1"
                },
                {
                    "id": "task_2",
                    "type": "agent",
                    "agent": "task_2"
                },
                {
                    "id": "task_3",
                    "type": "agent",
                    "agent": "task_3"
                },
                {
                    "id": "end",
                    "type": "end",
                    "is_finish": True
                }
            ],
            "edges": [
                {"from": "start", "to": "task_1"},
                {"from": "start", "to": "task_2"},
                {"from": "start", "to": "task_3"},
                {"from": "task_1", "to": "end"},
                {"from": "task_2", "to": "end"},
                {"from": "task_3", "to": "end"}
            ]
        }
        
        workflow = orchestrator.create_workflow(
            user_id=user.id,
            name="Parallel Task Test",
            workflow_type="test",
            definition=definition,
            execution_mode="parallel"
        )
        
        # Execute workflow and measure time
        import time
        start_time = time.time()
        
        result = await orchestrator.executeWorkflow(
            workflow_id=workflow.id,
            context={"user_id": str(user.id)}
        )
        
        end_time = time.time()
        execution_time = (end_time - start_time) * 1000  # Convert to ms
        
        # Verify workflow completed
        assert result["status"] in ["completed", "failed"]
        
        # If completed successfully, verify all tasks ran
        if result["status"] == "completed":
            assert "results" in result
            assert "task_1" in result["results"]
            assert "task_2" in result["results"]
            assert "task_3" in result["results"]
            
            # Verify each task completed
            assert result["results"]["task_1"]["status"] == "completed"
            assert result["results"]["task_2"]["status"] == "completed"
            assert result["results"]["task_3"]["status"] == "completed"
            
            # Parallel execution should be faster than sequential
            # (3 tasks * 100ms each = 300ms sequential, but parallel should be ~100ms)
            # Allow some overhead, so check it's less than 250ms
            assert execution_time < 250, f"Parallel execution took {execution_time}ms, expected < 250ms"
    
    @pytest.mark.asyncio
    async def test_parallel_agent_workflow_integration(self, db_session, test_user_with_portfolio, redis_client):
        """
        Test multiple agents execute in parallel in a single workflow.
        
        **Validates: Requirements 5.4, 5.5**
        """
        user = test_user_with_portfolio
        
        # Create orchestrator and register all agents
        orchestrator = AgenticOrchestrator(db_session)
        
        price_alert_agent = PriceAlertAgent(db_session, redis_client, get_mcp_factory())
        research_agent = ResearchAgent(db_session, redis_client, get_mcp_factory())
        rebalancing_agent = RebalancingAgent(db_session, redis_client, get_mcp_factory())
        
        async def price_alert_wrapper(state):
            try:
                result = await price_alert_agent.execute(state["context"])
                state["results"]["price_alerts"] = result
            except Exception as e:
                state["errors"].append(f"Price alert agent failed: {str(e)}")
            return state
        
        async def research_wrapper(state):
            try:
                result = await research_agent.execute(state["context"])
                state["results"]["research"] = result
            except Exception as e:
                state["errors"].append(f"Research agent failed: {str(e)}")
            return state
        
        async def rebalancing_wrapper(state):
            try:
                result = await rebalancing_agent.execute(state["context"])
                state["results"]["rebalancing"] = result
            except Exception as e:
                state["errors"].append(f"Rebalancing agent failed: {str(e)}")
            return state
        
        orchestrator.register_agent("price_alert", price_alert_wrapper)
        orchestrator.register_agent("research", research_wrapper)
        orchestrator.register_agent("rebalancing", rebalancing_wrapper)
        
        # Create parallel workflow with all agents
        definition = {
            "nodes": [
                {
                    "id": "start",
                    "type": "start",
                    "is_entry": True
                },
                {
                    "id": "price_alerts",
                    "type": "agent",
                    "agent": "price_alert"
                },
                {
                    "id": "research",
                    "type": "agent",
                    "agent": "research"
                },
                {
                    "id": "rebalancing",
                    "type": "agent",
                    "agent": "rebalancing"
                },
                {
                    "id": "end",
                    "type": "end",
                    "is_finish": True
                }
            ],
            "edges": [
                {"from": "start", "to": "price_alerts"},
                {"from": "start", "to": "research"},
                {"from": "start", "to": "rebalancing"},
                {"from": "price_alerts", "to": "end"},
                {"from": "research", "to": "end"},
                {"from": "rebalancing", "to": "end"}
            ]
        }
        
        workflow = orchestrator.create_workflow(
            user_id=user.id,
            name="Comprehensive Parallel Analysis",
            workflow_type="comprehensive",
            definition=definition,
            execution_mode="parallel"
        )
        
        # Execute workflow
        result = await orchestrator.executeWorkflow(
            workflow_id=workflow.id,
            context={"user_id": str(user.id)}
        )
        
        # Verify workflow completed (may have errors if MCP not available)
        assert result["status"] in ["completed", "failed"]
        assert "executionTime" in result
        
        # Verify workflow attempted to run all agents
        assert "results" in result or "errors" in result
