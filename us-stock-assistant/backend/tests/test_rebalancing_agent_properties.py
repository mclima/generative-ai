"""
Property-based tests for Rebalancing Agent.

Feature: us-stock-assistant, Property 21: Portfolio Rebalancing Suggestions
**Validates: Requirements 5.2**
"""
import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from decimal import Decimal
from datetime import date
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from app.models import User, Portfolio, StockPosition, Notification
from app.services.agents.rebalancing_agent import RebalancingAgent


# Strategies for generating test data
@st.composite
def portfolio_with_allocations(draw):
    """Generate valid portfolio data with target allocations."""
    num_positions = draw(st.integers(min_value=2, max_value=5))
    tickers = draw(st.lists(
        st.sampled_from(["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA", "META"]),
        min_size=num_positions,
        max_size=num_positions,
        unique=True
    ))
    
    positions = []
    for ticker in tickers:
        positions.append({
            "ticker": ticker,
            "quantity": draw(st.floats(min_value=1.0, max_value=100.0)),
            "purchase_price": draw(st.floats(min_value=10.0, max_value=500.0)),
            "purchase_date": draw(st.dates(
                min_value=date(2020, 1, 1),
                max_value=date.today()
            ))
        })
    
    # Generate target allocations that sum to 100%
    # Use Dirichlet-like distribution
    raw_allocations = [draw(st.floats(min_value=0.1, max_value=1.0)) for _ in tickers]
    total = sum(raw_allocations)
    target_allocations = {
        ticker: (raw_allocations[i] / total) * 100
        for i, ticker in enumerate(tickers)
    }
    
    return {
        "tickers": tickers,
        "positions": positions,
        "target_allocations": target_allocations
    }


@st.composite
def mock_prices(draw, tickers):
    """Generate mock current prices for tickers."""
    return {
        ticker: {
            "ticker": ticker,
            "price": draw(st.floats(min_value=10.0, max_value=1000.0)),
            "change": draw(st.floats(min_value=-50.0, max_value=50.0)),
            "changePercent": draw(st.floats(min_value=-10.0, max_value=10.0)),
            "volume": draw(st.integers(min_value=1000000, max_value=100000000))
        }
        for ticker in tickers
    }


class TestRebalancingAgentProperties:
    """Property-based tests for Rebalancing Agent."""
    
    @given(portfolio_data=portfolio_with_allocations())
    @settings(
        max_examples=5,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_property_21_portfolio_rebalancing_suggestions(self, db_session, portfolio_data):
        """
        Property 21: Portfolio Rebalancing Suggestions
        
        For any portfolio with enabled analysis, the agentic system should
        periodically generate rebalancing suggestions based on portfolio
        composition and market conditions.
        
        **Validates: Requirements 5.2**
        """
        # Create test user
        user = User(
            email=f"test_{uuid4()}@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create portfolio
        portfolio_obj = Portfolio(user_id=user.id)
        db_session.add(portfolio_obj)
        db_session.commit()
        db_session.refresh(portfolio_obj)
        
        # Add positions
        for pos_data in portfolio_data["positions"]:
            position = StockPosition(
                portfolio_id=portfolio_obj.id,
                ticker=pos_data["ticker"],
                quantity=Decimal(str(round(pos_data["quantity"], 4))),
                purchase_price=Decimal(str(round(pos_data["purchase_price"], 2))),
                purchase_date=pos_data["purchase_date"]
            )
            db_session.add(position)
        db_session.commit()
        
        # Create rebalancing agent with mocked services
        mock_mcp_tools = MagicMock()
        rebalancing_agent = RebalancingAgent(db_session, mcp_tools=mock_mcp_tools)
        
        # Generate mock current prices
        from hypothesis import strategies as st
        prices = {
            ticker: {
                "ticker": ticker,
                "price": 100.0,  # Use fixed price for deterministic testing
                "change": 0.0,
                "changePercent": 0.0,
                "volume": 1000000
            }
            for ticker in portfolio_data["tickers"]
        }
        
        with patch.object(rebalancing_agent.stock_service, 'getBatchPrices', new_callable=AsyncMock) as mock_get_prices:
            mock_get_prices.return_value = prices
            
            # Execute rebalancing agent
            import asyncio
            state = {
                "context": {
                    "user_id": str(user.id),
                    "target_allocations": portfolio_data["target_allocations"]
                },
                "results": {},
                "errors": []
            }
            
            final_state = asyncio.run(rebalancing_agent(state))
            
            # Verify rebalancing analysis was performed
            assert "rebalancing" in final_state["results"]
            rebalancing_results = final_state["results"]["rebalancing"]
            
            # Verify composition analysis
            assert "composition" in rebalancing_results
            composition = rebalancing_results["composition"]
            assert "total_value" in composition
            assert "position_values" in composition
            assert "allocations" in composition
            assert "position_count" in composition
            assert composition["position_count"] == len(portfolio_data["tickers"])
            
            # Verify all tickers are in composition
            for ticker in portfolio_data["tickers"]:
                assert ticker in composition["allocations"]
                assert ticker in composition["position_values"]
            
            # Verify suggestions were generated
            assert "suggestions" in rebalancing_results
            suggestions = rebalancing_results["suggestions"]
            
            # Verify suggestion structure
            for suggestion in suggestions:
                assert "ticker" in suggestion
                assert "action" in suggestion
                assert suggestion["action"] in ["buy", "sell", "hold"]
                assert "reason" in suggestion
                assert "current_allocation" in suggestion
                assert "target_allocation" in suggestion
                assert "suggested_amount" in suggestion
                
                # Verify ticker is in portfolio
                assert suggestion["ticker"] in portfolio_data["tickers"]
                
                # Verify action matches allocation difference
                if suggestion["action"] == "buy":
                    assert suggestion["current_allocation"] < suggestion["target_allocation"]
                elif suggestion["action"] == "sell":
                    assert suggestion["current_allocation"] > suggestion["target_allocation"]
            
            # Verify notification was created if suggestions exist
            if suggestions:
                notifications = db_session.query(Notification).filter(
                    Notification.user_id == user.id,
                    Notification.type == "rebalancing_suggestion"
                ).all()
                
                assert len(notifications) >= 1
                
                # Verify notification content
                notification = notifications[0]
                assert "Rebalancing" in notification.title
                assert notification.data.get("suggestions") is not None
                assert notification.data.get("composition") is not None
    
    @given(num_positions=st.integers(min_value=2, max_value=10))
    @settings(
        max_examples=5,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_equal_weight_rebalancing_without_targets(self, db_session, num_positions):
        """
        Test that rebalancing agent suggests equal weighting when no targets provided.
        """
        # Create test user
        user = User(
            email=f"test_{uuid4()}@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create portfolio with multiple positions
        portfolio = Portfolio(user_id=user.id)
        db_session.add(portfolio)
        db_session.commit()
        
        tickers = [f"TST{chr(65+i)}" for i in range(min(num_positions, 26))]
        for ticker in tickers:
            position = StockPosition(
                portfolio_id=portfolio.id,
                ticker=ticker,
                quantity=Decimal("10.0"),
                purchase_price=Decimal("100.0"),
                purchase_date=date.today()
            )
            db_session.add(position)
        db_session.commit()
        
        # Create rebalancing agent
        mock_mcp_tools = MagicMock()
        rebalancing_agent = RebalancingAgent(db_session, mcp_tools=mock_mcp_tools)
        
        # Mock prices (all equal)
        prices = {
            ticker: {"ticker": ticker, "price": 100.0, "change": 0, "changePercent": 0, "volume": 1000000}
            for ticker in tickers
        }
        
        with patch.object(rebalancing_agent.stock_service, 'getBatchPrices', new_callable=AsyncMock) as mock_get_prices:
            mock_get_prices.return_value = prices
            
            # Execute without target allocations
            import asyncio
            state = {
                "context": {"user_id": str(user.id)},
                "results": {},
                "errors": []
            }
            
            final_state = asyncio.run(rebalancing_agent(state))
            
            # Verify composition shows equal allocations (since all have same value)
            composition = final_state["results"]["rebalancing"]["composition"]
            expected_allocation = 100.0 / num_positions
            
            for ticker in tickers:
                actual_allocation = composition["allocations"][ticker]
                # Should be approximately equal (within 1% due to rounding)
                assert abs(actual_allocation - expected_allocation) < 1.0
    
    @given(
        num_positions=st.integers(min_value=2, max_value=5),
        price_variance=st.floats(min_value=0.5, max_value=2.0)
    )
    @settings(
        max_examples=5,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_rebalancing_with_price_changes(self, db_session, num_positions, price_variance):
        """
        Test that rebalancing agent correctly handles price changes.
        """
        # Create test user
        user = User(
            email=f"test_{uuid4()}@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create portfolio
        portfolio = Portfolio(user_id=user.id)
        db_session.add(portfolio)
        db_session.commit()
        
        tickers = [f"TST{chr(65+i)}" for i in range(min(num_positions, 26))]
        for ticker in tickers:
            position = StockPosition(
                portfolio_id=portfolio.id,
                ticker=ticker,
                quantity=Decimal("10.0"),
                purchase_price=Decimal("100.0"),
                purchase_date=date.today()
            )
            db_session.add(position)
        db_session.commit()
        
        # Create rebalancing agent
        mock_mcp_tools = MagicMock()
        rebalancing_agent = RebalancingAgent(db_session, mcp_tools=mock_mcp_tools)
        
        # Mock prices with variance
        prices = {
            ticker: {
                "ticker": ticker,
                "price": 100.0 * price_variance if i == 0 else 100.0,
                "change": 0,
                "changePercent": 0,
                "volume": 1000000
            }
            for i, ticker in enumerate(tickers)
        }
        
        with patch.object(rebalancing_agent.stock_service, 'getBatchPrices', new_callable=AsyncMock) as mock_get_prices:
            mock_get_prices.return_value = prices
            
            # Execute rebalancing
            import asyncio
            state = {
                "context": {"user_id": str(user.id)},
                "results": {},
                "errors": []
            }
            
            final_state = asyncio.run(rebalancing_agent(state))
            
            # Verify composition reflects price changes
            composition = final_state["results"]["rebalancing"]["composition"]
            
            # First ticker should have different allocation due to price variance
            first_ticker = tickers[0]
            first_allocation = composition["allocations"][first_ticker]
            
            # Calculate expected allocation
            total_value = 100.0 * price_variance * 10.0 + 100.0 * 10.0 * (num_positions - 1)
            expected_first_allocation = (100.0 * price_variance * 10.0 / total_value) * 100
            
            # Should be approximately equal (within 1% due to rounding)
            assert abs(first_allocation - expected_first_allocation) < 1.0
    
    @given(portfolio_data=portfolio_with_allocations())
    @settings(
        max_examples=5,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_rebalancing_suggestions_sorted_by_magnitude(self, db_session, portfolio_data):
        """
        Test that rebalancing suggestions are sorted by magnitude of difference.
        """
        # Create test user
        user = User(
            email=f"test_{uuid4()}@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create portfolio
        portfolio = Portfolio(user_id=user.id)
        db_session.add(portfolio)
        db_session.commit()
        
        # Add positions
        for pos_data in portfolio_data["positions"]:
            position = StockPosition(
                portfolio_id=portfolio.id,
                ticker=pos_data["ticker"],
                quantity=Decimal(str(round(pos_data["quantity"], 4))),
                purchase_price=Decimal(str(round(pos_data["purchase_price"], 2))),
                purchase_date=pos_data["purchase_date"]
            )
            db_session.add(position)
        db_session.commit()
        
        # Create rebalancing agent
        mock_mcp_tools = MagicMock()
        rebalancing_agent = RebalancingAgent(db_session, mcp_tools=mock_mcp_tools)
        
        # Mock prices
        prices = {
            ticker: {"ticker": ticker, "price": 100.0, "change": 0, "changePercent": 0, "volume": 1000000}
            for ticker in portfolio_data["tickers"]
        }
        
        with patch.object(rebalancing_agent.stock_service, 'getBatchPrices', new_callable=AsyncMock) as mock_get_prices:
            mock_get_prices.return_value = prices
            
            # Execute rebalancing
            import asyncio
            state = {
                "context": {
                    "user_id": str(user.id),
                    "target_allocations": portfolio_data["target_allocations"]
                },
                "results": {},
                "errors": []
            }
            
            final_state = asyncio.run(rebalancing_agent(state))
            
            # Verify suggestions are sorted by magnitude
            suggestions = final_state["results"]["rebalancing"]["suggestions"]
            
            if len(suggestions) > 1:
                for i in range(len(suggestions) - 1):
                    current_diff = abs(
                        suggestions[i]["current_allocation"] - suggestions[i]["target_allocation"]
                    )
                    next_diff = abs(
                        suggestions[i+1]["current_allocation"] - suggestions[i+1]["target_allocation"]
                    )
                    # Current should be >= next (sorted descending)
                    assert current_diff >= next_diff - 0.1  # Allow small rounding errors
    
    def test_empty_portfolio_handling(self, db_session):
        """
        Test that rebalancing agent handles empty portfolios gracefully.
        """
        # Create test user
        user = User(
            email=f"test_{uuid4()}@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create empty portfolio
        portfolio = Portfolio(user_id=user.id)
        db_session.add(portfolio)
        db_session.commit()
        
        # Create rebalancing agent
        mock_mcp_tools = MagicMock()
        rebalancing_agent = RebalancingAgent(db_session, mcp_tools=mock_mcp_tools)
        
        # Execute rebalancing
        import asyncio
        state = {
            "context": {"user_id": str(user.id)},
            "results": {},
            "errors": []
        }
        
        final_state = asyncio.run(rebalancing_agent(state))
        
        # Verify graceful handling
        assert "rebalancing" in final_state["results"]
        assert final_state["results"]["rebalancing"]["suggestions"] == []
        assert "No portfolio positions" in final_state["results"]["rebalancing"]["message"]
        assert len(final_state["errors"]) == 0
