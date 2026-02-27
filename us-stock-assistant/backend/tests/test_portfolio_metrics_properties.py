"""
Property-based tests for portfolio metrics.

Tests:
- Property 7: Portfolio Metric Consistency
- Property 8: Portfolio Diversity Calculation
- Property 9: Performance Period Completeness
"""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck, assume
from datetime import date, timedelta
from decimal import Decimal
import uuid
from sqlalchemy.orm import Session

from app.models import User, Portfolio, StockPosition
from app.services.portfolio_service import PortfolioService


# Custom strategies for generating test data
@st.composite
def valid_ticker_strategy(draw):
    """Generate valid ticker symbols."""
    length = draw(st.integers(min_value=1, max_value=5))
    ticker = ''.join(draw(st.lists(st.sampled_from('ABCDEFGHIJKLMNOPQRSTUVWXYZ'), min_size=length, max_size=length)))
    return ticker


@st.composite
def stock_position_data_strategy(draw):
    """Generate valid stock position data."""
    ticker = draw(valid_ticker_strategy())
    quantity = draw(st.decimals(min_value=Decimal('0.0001'), max_value=Decimal('1000'), places=4))
    purchase_price = draw(st.decimals(min_value=Decimal('0.01'), max_value=Decimal('1000'), places=2))
    
    # Generate a date in the past (not future)
    days_ago = draw(st.integers(min_value=1, max_value=365))
    purchase_date = date.today() - timedelta(days=days_ago)
    
    return {
        'ticker': ticker,
        'quantity': quantity,
        'purchase_price': purchase_price,
        'purchase_date': purchase_date
    }


@st.composite
def user_data_strategy(draw):
    """Generate valid user data with unique email."""
    # Generate unique email using UUID to avoid collisions
    unique_id = str(uuid.uuid4())[:8]
    base_email = draw(st.from_regex(r'^[a-z0-9]+@[a-z]+\.[a-z]{2,}$', fullmatch=True))
    email = f"{unique_id}_{base_email}"
    password_hash = draw(st.text(alphabet=st.characters(blacklist_categories=('Cs',)), min_size=10, max_size=100))
    return {
        'email': email,
        'password_hash': password_hash
    }


class MockStockPrice:
    """Mock stock price for testing."""
    def __init__(self, ticker: str, price: float, change: float = 0.0, change_percent: float = 0.0):
        self.ticker = ticker
        self.price = price
        self.change = change
        self.change_percent = change_percent
        self.volume = 1000000
        self.timestamp = date.today()


class MockStockDataTools:
    """Mock stock data tools for testing."""
    def __init__(self, price_multiplier: float = 1.0):
        self.price_multiplier = price_multiplier
        self.prices = {}
    
    def set_price(self, ticker: str, price: float):
        """Set a specific price for a ticker."""
        self.prices[ticker] = price
    
    async def get_stock_price(self, ticker: str):
        """Get mock stock price."""
        if ticker in self.prices:
            price = self.prices[ticker]
        else:
            # Generate a mock price based on ticker hash
            price = 100.0 * self.price_multiplier
        
        return MockStockPrice(
            ticker=ticker,
            price=price,
            change=price * 0.01,  # 1% daily change
            change_percent=1.0
        )
    
    async def get_historical_data(self, ticker: str, start_date: date, end_date: date):
        """Get mock historical data."""
        return []


class TestPortfolioMetricConsistency:
    """Test portfolio metric consistency."""
    
    @given(
        user_data=user_data_strategy(),
        position_data=stock_position_data_strategy()
    )
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.asyncio
    async def test_property_7_portfolio_metric_consistency_add(
        self,
        db_session: Session,
        user_data: dict,
        position_data: dict
    ):
        """
        **Property 7: Portfolio Metric Consistency (Add Position)**
        
        For any portfolio with stock positions, when a position is added,
        the portfolio's total value, gain/loss, and percentage return should
        be recalculated and remain mathematically consistent with the sum
        of individual positions.
        
        **Validates: Requirements 2.3, 2.4, 2.5, 9.1, 9.2, 9.3**
        """
        # Ensure clean session state
        db_session.rollback()
        
        # Create user
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create portfolio service
        portfolio_service = PortfolioService(db_session)
        
        # Create mock stock data tools
        mock_tools = MockStockDataTools(price_multiplier=1.1)  # 10% gain
        
        # Calculate metrics for empty portfolio
        metrics_before = await portfolio_service.calculate_metrics(user.id, mock_tools)
        assert metrics_before["total_value"] == Decimal("0.00")
        
        # Add position
        position = portfolio_service.add_position(
            user_id=user.id,
            ticker=position_data['ticker'],
            quantity=position_data['quantity'],
            purchase_price=position_data['purchase_price'],
            purchase_date=position_data['purchase_date']
        )
        
        # Calculate metrics after adding position
        metrics_after = await portfolio_service.calculate_metrics(user.id, mock_tools)
        
        # Verify metrics are consistent
        expected_cost = position_data['quantity'] * position_data['purchase_price']
        
        # Get the mock price
        mock_price_data = await mock_tools.get_stock_price(position_data['ticker'])
        expected_value = position_data['quantity'] * Decimal(str(mock_price_data.price))
        expected_gain_loss = expected_value - expected_cost
        
        # Allow small rounding differences
        assert abs(metrics_after["total_value"] - expected_value) < Decimal("0.01")
        assert abs(metrics_after["total_gain_loss"] - expected_gain_loss) < Decimal("0.01")
        
        # Verify percentage is calculated correctly
        if expected_cost > 0:
            expected_percent = (expected_gain_loss / expected_cost * Decimal("100"))
            assert abs(metrics_after["total_gain_loss_percent"] - expected_percent) < Decimal("0.01")
    
    @given(
        user_data=user_data_strategy(),
        position_data_list=st.lists(stock_position_data_strategy(), min_size=2, max_size=5)
    )
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.asyncio
    async def test_property_7_portfolio_metric_consistency_multiple(
        self,
        db_session: Session,
        user_data: dict,
        position_data_list: list
    ):
        """
        Test that metrics remain consistent with multiple positions.
        
        **Validates: Requirements 2.3, 2.4, 2.5, 9.1, 9.2, 9.3**
        """
        # Ensure clean session state
        db_session.rollback()
        
        # Create user
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create portfolio service
        portfolio_service = PortfolioService(db_session)
        
        # Create mock stock data tools with specific prices
        mock_tools = MockStockDataTools()
        
        # Add positions and track expected values
        total_expected_cost = Decimal("0.00")
        total_expected_value = Decimal("0.00")
        
        for position_data in position_data_list:
            # Set a specific price for this ticker
            mock_price = float(position_data['purchase_price']) * 1.05  # 5% gain
            mock_tools.set_price(position_data['ticker'], mock_price)
            
            # Add position
            portfolio_service.add_position(
                user_id=user.id,
                ticker=position_data['ticker'],
                quantity=position_data['quantity'],
                purchase_price=position_data['purchase_price'],
                purchase_date=position_data['purchase_date']
            )
            
            # Track expected values
            total_expected_cost += position_data['quantity'] * position_data['purchase_price']
            total_expected_value += position_data['quantity'] * Decimal(str(mock_price))
        
        # Calculate metrics
        metrics = await portfolio_service.calculate_metrics(user.id, mock_tools)
        
        # Verify total value matches sum of individual positions
        assert abs(metrics["total_value"] - total_expected_value) < Decimal("0.01")
        
        # Verify gain/loss is consistent
        expected_gain_loss = total_expected_value - total_expected_cost
        assert abs(metrics["total_gain_loss"] - expected_gain_loss) < Decimal("0.01")
        
        # Verify percentage is consistent
        if total_expected_cost > 0:
            expected_percent = (expected_gain_loss / total_expected_cost * Decimal("100"))
            assert abs(metrics["total_gain_loss_percent"] - expected_percent) < Decimal("0.01")
    
    @given(
        user_data=user_data_strategy(),
        position_data=stock_position_data_strategy(),
        new_quantity=st.decimals(min_value=Decimal('0.0001'), max_value=Decimal('1000'), places=4)
    )
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.asyncio
    async def test_property_7_portfolio_metric_consistency_update(
        self,
        db_session: Session,
        user_data: dict,
        position_data: dict,
        new_quantity: Decimal
    ):
        """
        Test that metrics remain consistent when a position is updated.
        
        **Validates: Requirements 2.3, 2.4, 2.5, 9.1, 9.2, 9.3**
        """
        # Ensure clean session state
        db_session.rollback()
        
        # Create user
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create portfolio service
        portfolio_service = PortfolioService(db_session)
        
        # Create mock stock data tools
        mock_tools = MockStockDataTools()
        mock_price = float(position_data['purchase_price']) * 1.1
        mock_tools.set_price(position_data['ticker'], mock_price)
        
        # Add position
        position = portfolio_service.add_position(
            user_id=user.id,
            ticker=position_data['ticker'],
            quantity=position_data['quantity'],
            purchase_price=position_data['purchase_price'],
            purchase_date=position_data['purchase_date']
        )
        
        # Update position quantity
        portfolio_service.update_position(
            user_id=user.id,
            position_id=position.id,
            quantity=new_quantity
        )
        
        # Calculate metrics after update
        metrics = await portfolio_service.calculate_metrics(user.id, mock_tools)
        
        # Verify metrics reflect the updated quantity
        expected_cost = new_quantity * position_data['purchase_price']
        expected_value = new_quantity * Decimal(str(mock_price))
        expected_gain_loss = expected_value - expected_cost
        
        assert abs(metrics["total_value"] - expected_value) < Decimal("0.01")
        assert abs(metrics["total_gain_loss"] - expected_gain_loss) < Decimal("0.01")
    
    @given(
        user_data=user_data_strategy(),
        position_data_list=st.lists(stock_position_data_strategy(), min_size=2, max_size=5)
    )
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.asyncio
    async def test_property_7_portfolio_metric_consistency_remove(
        self,
        db_session: Session,
        user_data: dict,
        position_data_list: list
    ):
        """
        Test that metrics remain consistent when a position is removed.
        
        **Validates: Requirements 2.3, 2.4, 2.5, 9.1, 9.2, 9.3**
        """
        # Ensure clean session state
        db_session.rollback()
        
        # Create user
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create portfolio service
        portfolio_service = PortfolioService(db_session)
        
        # Create mock stock data tools
        mock_tools = MockStockDataTools()
        
        # Add positions
        positions = []
        for position_data in position_data_list:
            mock_price = float(position_data['purchase_price']) * 1.05
            mock_tools.set_price(position_data['ticker'], mock_price)
            
            position = portfolio_service.add_position(
                user_id=user.id,
                ticker=position_data['ticker'],
                quantity=position_data['quantity'],
                purchase_price=position_data['purchase_price'],
                purchase_date=position_data['purchase_date']
            )
            positions.append((position, position_data))
        
        # Remove first position
        position_to_remove, removed_data = positions[0]
        portfolio_service.remove_position(user.id, position_to_remove.id)
        
        # Calculate expected values for remaining positions
        total_expected_cost = Decimal("0.00")
        total_expected_value = Decimal("0.00")
        
        for position, position_data in positions[1:]:
            mock_price = await mock_tools.get_stock_price(position_data['ticker'])
            total_expected_cost += position_data['quantity'] * position_data['purchase_price']
            total_expected_value += position_data['quantity'] * Decimal(str(mock_price.price))
        
        # Calculate metrics after removal
        metrics = await portfolio_service.calculate_metrics(user.id, mock_tools)
        
        # Verify metrics reflect the removal
        assert abs(metrics["total_value"] - total_expected_value) < Decimal("0.01")
        
        expected_gain_loss = total_expected_value - total_expected_cost
        assert abs(metrics["total_gain_loss"] - expected_gain_loss) < Decimal("0.01")


class TestPortfolioDiversity:
    """Test portfolio diversity calculation."""
    
    @given(
        user_data=user_data_strategy(),
        position_data=stock_position_data_strategy()
    )
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.asyncio
    async def test_property_8_single_position_zero_diversity(
        self,
        db_session: Session,
        user_data: dict,
        position_data: dict
    ):
        """
        **Property 8: Portfolio Diversity Calculation (Single Position)**
        
        For any portfolio with a single stock, the diversity score should be 0.
        
        **Validates: Requirements 9.4**
        """
        # Ensure clean session state
        db_session.rollback()
        
        # Create user
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create portfolio service
        portfolio_service = PortfolioService(db_session)
        
        # Add single position
        portfolio_service.add_position(
            user_id=user.id,
            ticker=position_data['ticker'],
            quantity=position_data['quantity'],
            purchase_price=position_data['purchase_price'],
            purchase_date=position_data['purchase_date']
        )
        
        # Calculate metrics
        mock_tools = MockStockDataTools()
        metrics = await portfolio_service.calculate_metrics(user.id, mock_tools)
        
        # Verify diversity score is 0 for single position
        assert metrics["diversity_score"] == Decimal("0.00")
    
    @given(
        user_data=user_data_strategy(),
        num_positions=st.integers(min_value=2, max_value=10)
    )
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.asyncio
    async def test_property_8_equal_positions_high_diversity(
        self,
        db_session: Session,
        user_data: dict,
        num_positions: int
    ):
        """
        **Property 8: Portfolio Diversity Calculation (Equal Distribution)**
        
        For any portfolio with multiple stocks of equal value, the diversity
        score should be higher than for concentrated portfolios.
        
        **Validates: Requirements 9.4**
        """
        # Ensure clean session state
        db_session.rollback()
        
        # Create user
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create portfolio service
        portfolio_service = PortfolioService(db_session)
        
        # Create mock stock data tools
        mock_tools = MockStockDataTools()
        
        # Add equal-value positions
        equal_quantity = Decimal("10.0")
        equal_price = Decimal("100.00")
        
        # Generate unique ticker symbols (letters only, no numbers)
        ticker_prefixes = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J']
        
        for i in range(num_positions):
            ticker = ticker_prefixes[i] if i < len(ticker_prefixes) else f"TICK{chr(65 + i)}"
            mock_tools.set_price(ticker, float(equal_price))
            
            portfolio_service.add_position(
                user_id=user.id,
                ticker=ticker,
                quantity=equal_quantity,
                purchase_price=equal_price,
                purchase_date=date.today() - timedelta(days=30)
            )
        
        # Calculate metrics
        metrics = await portfolio_service.calculate_metrics(user.id, mock_tools)
        
        # Verify diversity score is high (close to 1.0) for equal distribution
        # With equal distribution, diversity should be close to 1.0
        assert metrics["diversity_score"] >= Decimal("0.80")


class TestPerformancePeriodCompleteness:
    """Test performance period completeness."""
    
    @given(
        user_data=user_data_strategy(),
        position_data=stock_position_data_strategy()
    )
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.asyncio
    async def test_property_9_performance_period_completeness(
        self,
        db_session: Session,
        user_data: dict,
        position_data: dict
    ):
        """
        **Property 9: Performance Period Completeness**
        
        For any portfolio, requesting performance metrics should return values
        for all specified time periods (1D, 1W, 1M, 3M, 1Y, ALL) without
        missing data.
        
        **Validates: Requirements 9.5**
        """
        # Ensure clean session state
        db_session.rollback()
        
        # Create user
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create portfolio service
        portfolio_service = PortfolioService(db_session)
        
        # Add position
        portfolio_service.add_position(
            user_id=user.id,
            ticker=position_data['ticker'],
            quantity=position_data['quantity'],
            purchase_price=position_data['purchase_price'],
            purchase_date=position_data['purchase_date']
        )
        
        # Calculate metrics
        mock_tools = MockStockDataTools()
        metrics = await portfolio_service.calculate_metrics(user.id, mock_tools)
        
        # Verify all periods are present
        required_periods = ["1D", "1W", "1M", "3M", "1Y", "ALL"]
        performance = metrics["performance_by_period"]
        
        for period in required_periods:
            assert period in performance, f"Missing period: {period}"
            assert isinstance(performance[period], Decimal), f"Period {period} should be Decimal"
            # Verify it's a valid number (not None or NaN)
            assert performance[period] is not None
    
    @given(
        user_data=user_data_strategy(),
        position_data_list=st.lists(stock_position_data_strategy(), min_size=1, max_size=5)
    )
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    @pytest.mark.asyncio
    async def test_property_9_all_period_matches_total_return(
        self,
        db_session: Session,
        user_data: dict,
        position_data_list: list
    ):
        """
        Test that the ALL period matches the total return calculation.
        
        **Validates: Requirements 9.5**
        """
        # Ensure clean session state
        db_session.rollback()
        
        # Create user
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create portfolio service
        portfolio_service = PortfolioService(db_session)
        
        # Create mock stock data tools
        mock_tools = MockStockDataTools()
        
        # Add positions
        for position_data in position_data_list:
            mock_price = float(position_data['purchase_price']) * 1.15  # 15% gain
            mock_tools.set_price(position_data['ticker'], mock_price)
            
            portfolio_service.add_position(
                user_id=user.id,
                ticker=position_data['ticker'],
                quantity=position_data['quantity'],
                purchase_price=position_data['purchase_price'],
                purchase_date=position_data['purchase_date']
            )
        
        # Calculate metrics
        metrics = await portfolio_service.calculate_metrics(user.id, mock_tools)
        
        # Verify ALL period matches total gain/loss percent
        all_period_return = metrics["performance_by_period"]["ALL"]
        total_return = metrics["total_gain_loss_percent"]
        
        assert abs(all_period_return - total_return) < Decimal("0.01")
