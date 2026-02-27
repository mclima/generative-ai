"""
Tests for workflow orchestration functionality.
"""
import pytest
from uuid import uuid4
from datetime import datetime
from sqlalchemy.orm import Session

from app.services.agentic_orchestrator import AgenticOrchestrator
from app.services.workflow_definitions import (
    get_price_monitoring_workflow,
    get_research_workflow,
    get_rebalancing_workflow,
    get_comprehensive_analysis_workflow,
    get_parallel_monitoring_workflow,
    list_workflow_templates
)
from app.models import User, Portfolio, StockPosition, Workflow


@pytest.fixture
def test_user(db_session: Session):
    """Create a test user with portfolio."""
    user = User(
        email="test@example.com",
        password_hash="hashed_password"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    
    # Create portfolio with positions
    portfolio = Portfolio(user_id=user.id)
    db_session.add(portfolio)
    db_session.commit()
    db_session.refresh(portfolio)
    
    # Add some positions
    positions = [
        StockPosition(
            portfolio_id=portfolio.id,
            ticker="AAPL",
            quantity=10,
            purchase_price=150.00,
            purchase_date=datetime(2024, 1, 1).date()
        ),
        StockPosition(
            portfolio_id=portfolio.id,
            ticker="GOOGL",
            quantity=5,
            purchase_price=140.00,
            purchase_date=datetime(2024, 1, 1).date()
        )
    ]
    for pos in positions:
        db_session.add(pos)
    db_session.commit()
    
    return user


def test_workflow_definitions():
    """Test that workflow definitions are properly structured."""
    # Test price monitoring workflow
    price_workflow = get_price_monitoring_workflow()
    assert "nodes" in price_workflow
    assert "edges" in price_workflow
    assert len(price_workflow["nodes"]) > 0
    
    # Test research workflow
    research_workflow = get_research_workflow()
    assert "nodes" in research_workflow
    assert "edges" in research_workflow
    
    # Test rebalancing workflow
    rebalancing_workflow = get_rebalancing_workflow()
    assert "nodes" in rebalancing_workflow
    assert "edges" in rebalancing_workflow
    
    # Test comprehensive analysis workflow (sequential)
    comprehensive_workflow = get_comprehensive_analysis_workflow()
    assert "nodes" in comprehensive_workflow
    assert "edges" in comprehensive_workflow
    assert len(comprehensive_workflow["edges"]) > 0  # Should have connections
    
    # Test parallel monitoring workflow
    parallel_workflow = get_parallel_monitoring_workflow()
    assert "nodes" in parallel_workflow
    assert "edges" in parallel_workflow
    assert len(parallel_workflow["nodes"]) >= 3  # Should have multiple agent nodes


def test_list_workflow_templates():
    """Test listing workflow templates."""
    templates = list_workflow_templates()
    
    assert isinstance(templates, dict)
    assert len(templates) > 0
    
    # Check that expected templates exist
    assert "price_monitoring" in templates
    assert "research" in templates
    assert "rebalancing" in templates
    
    # Check template structure
    for name, template in templates.items():
        assert "name" in template
        assert "description" in template
        assert "execution_mode" in template
        assert "default_schedule" in template


def test_create_workflow_from_template(db_session: Session, test_user):
    """Test creating a workflow from a template."""
    orchestrator = AgenticOrchestrator(db_session)
    
    # Create workflow from template
    workflow = orchestrator.create_workflow_from_template(
        user_id=test_user.id,
        template_name="price_monitoring"
    )
    
    assert workflow.id is not None
    assert workflow.user_id == test_user.id
    assert workflow.workflow_type == "price_monitoring"
    assert workflow.execution_mode == "parallel"
    assert workflow.definition is not None
    assert "nodes" in workflow.definition


def test_create_custom_workflow(db_session: Session, test_user):
    """Test creating a custom workflow."""
    orchestrator = AgenticOrchestrator(db_session)
    
    # Create custom workflow
    definition = {
        "nodes": [
            {
                "id": "test_node",
                "type": "agent",
                "agent": "price_alert",
                "is_entry": True,
                "is_finish": True
            }
        ],
        "edges": []
    }
    
    workflow = orchestrator.create_workflow(
        user_id=test_user.id,
        name="Custom Test Workflow",
        workflow_type="custom",
        definition=definition,
        execution_mode="sequential"
    )
    
    assert workflow.id is not None
    assert workflow.name == "Custom Test Workflow"
    assert workflow.execution_mode == "sequential"


def test_get_user_workflows(db_session: Session, test_user):
    """Test retrieving user workflows."""
    orchestrator = AgenticOrchestrator(db_session)
    
    # Create multiple workflows
    orchestrator.create_workflow_from_template(
        user_id=test_user.id,
        template_name="price_monitoring"
    )
    orchestrator.create_workflow_from_template(
        user_id=test_user.id,
        template_name="research"
    )
    
    # Get user workflows
    workflows = orchestrator.get_user_workflows(test_user.id)
    
    assert len(workflows) == 2
    assert all(w.user_id == test_user.id for w in workflows)


@pytest.mark.asyncio
async def test_execute_workflow_basic(db_session: Session, test_user):
    """Test basic workflow execution."""
    orchestrator = AgenticOrchestrator(db_session)
    
    # Register a simple test agent
    async def test_agent(state):
        state["results"]["test"] = "success"
        return state
    
    orchestrator.register_agent("test_agent", test_agent)
    
    # Create a simple workflow
    definition = {
        "nodes": [
            {
                "id": "test",
                "type": "agent",
                "agent": "test_agent",
                "is_entry": True,
                "is_finish": True
            }
        ],
        "edges": []
    }
    
    workflow = orchestrator.create_workflow(
        user_id=test_user.id,
        name="Test Workflow",
        workflow_type="test",
        definition=definition,
        execution_mode="sequential"
    )
    
    # Execute workflow
    result = await orchestrator.executeWorkflow(
        workflow_id=workflow.id,
        context={"user_id": str(test_user.id)}
    )
    
    assert result["status"] in ["completed", "failed"]
    assert "executionTime" in result
    assert "results" in result


@pytest.mark.asyncio
async def test_schedule_workflow(db_session: Session, test_user):
    """Test scheduling a workflow."""
    orchestrator = AgenticOrchestrator(db_session)
    
    # Create workflow
    workflow = orchestrator.create_workflow_from_template(
        user_id=test_user.id,
        template_name="price_monitoring"
    )
    
    # Schedule workflow (every 5 minutes)
    job_id = await orchestrator.scheduleWorkflow(
        workflow_id=workflow.id,
        schedule="*/5 * * * *",
        context={"user_id": str(test_user.id)}
    )
    
    assert job_id is not None
    
    # Verify workflow is marked as active
    db_session.refresh(workflow)
    assert workflow.is_active is True
    assert workflow.schedule == "*/5 * * * *"
    
    # Cancel the workflow
    await orchestrator.cancelWorkflow(workflow.id)
    
    # Verify workflow is marked as inactive
    db_session.refresh(workflow)
    assert workflow.is_active is False


@pytest.mark.asyncio
async def test_get_workflow_status(db_session: Session, test_user):
    """Test getting workflow execution status."""
    orchestrator = AgenticOrchestrator(db_session)
    
    # Register a simple test agent
    async def test_agent(state):
        state["results"]["test"] = "success"
        return state
    
    orchestrator.register_agent("test_agent", test_agent)
    
    # Create and execute workflow
    definition = {
        "nodes": [
            {
                "id": "test",
                "type": "agent",
                "agent": "test_agent",
                "is_entry": True,
                "is_finish": True
            }
        ],
        "edges": []
    }
    
    workflow = orchestrator.create_workflow(
        user_id=test_user.id,
        name="Test Workflow",
        workflow_type="test",
        definition=definition,
        execution_mode="sequential"
    )
    
    result = await orchestrator.executeWorkflow(
        workflow_id=workflow.id,
        context={"user_id": str(test_user.id)}
    )
    
    # Get status
    execution_id = result["executionId"]
    status = await orchestrator.getWorkflowStatus(execution_id)
    
    assert status["executionId"] == execution_id
    assert status["status"] in ["completed", "failed"]
    assert "progress" in status


def test_sequential_vs_parallel_execution_modes(db_session: Session, test_user):
    """Test that sequential and parallel workflows are structured differently."""
    orchestrator = AgenticOrchestrator(db_session)
    
    # Create sequential workflow
    sequential_workflow = orchestrator.create_workflow_from_template(
        user_id=test_user.id,
        template_name="comprehensive_analysis"
    )
    assert sequential_workflow.execution_mode == "sequential"
    
    # Create parallel workflow
    parallel_workflow = orchestrator.create_workflow_from_template(
        user_id=test_user.id,
        template_name="parallel_monitoring"
    )
    assert parallel_workflow.execution_mode == "parallel"
    
    # Verify they have different structures
    assert sequential_workflow.definition != parallel_workflow.definition


def test_workflow_executions_history(db_session: Session, test_user):
    """Test retrieving workflow execution history."""
    orchestrator = AgenticOrchestrator(db_session)
    
    # Create workflow
    workflow = orchestrator.create_workflow_from_template(
        user_id=test_user.id,
        template_name="price_monitoring"
    )
    
    # Get executions (should be empty initially)
    executions = orchestrator.get_workflow_executions(workflow.id)
    assert len(executions) == 0
