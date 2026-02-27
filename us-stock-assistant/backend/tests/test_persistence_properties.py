"""
Property-based tests for data persistence layer.

Tests:
- Property 5: Portfolio Position Persistence Round-Trip
- Property 29: Concurrent Update Consistency
- Property 30: Persistence Retry Logic
"""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck, assume
from datetime import date, timedelta
from decimal import Decimal
import uuid
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import User, Portfolio, StockPosition
from app.validators import validate_ticker


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
    quantity = draw(st.decimals(min_value=Decimal('0.0001'), max_value=Decimal('10000'), places=4))
    purchase_price = draw(st.decimals(min_value=Decimal('0.01'), max_value=Decimal('10000'), places=2))
    
    # Generate a date in the past (not future)
    days_ago = draw(st.integers(min_value=0, max_value=3650))  # Up to 10 years ago
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


class TestPortfolioPersistence:
    """Test portfolio and stock position persistence."""
    
    @given(
        user_data=user_data_strategy(),
        position_data=stock_position_data_strategy()
    )
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_5_portfolio_position_persistence_round_trip(
        self,
        db_session: Session,
        user_data: dict,
        position_data: dict
    ):
        """
        **Property 5: Portfolio Position Persistence Round-Trip**
        
        For any valid stock position, adding it to a portfolio then retrieving 
        the portfolio should include that position with all original data intact.
        
        **Validates: Requirements 2.1, 7.2**
        """
        # Ensure clean session state
        db_session.rollback()
        
        # Create user
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create portfolio
        portfolio = Portfolio(user_id=user.id)
        db_session.add(portfolio)
        db_session.commit()
        db_session.refresh(portfolio)
        
        # Add stock position
        position = StockPosition(
            portfolio_id=portfolio.id,
            **position_data
        )
        db_session.add(position)
        db_session.commit()
        db_session.refresh(position)
        
        # Store original values
        original_id = position.id
        original_ticker = position.ticker
        original_quantity = position.quantity
        original_price = position.purchase_price
        original_date = position.purchase_date
        
        # Clear session to force fresh read from database
        db_session.expire_all()
        
        # Retrieve portfolio with positions
        retrieved_portfolio = db_session.query(Portfolio).filter_by(id=portfolio.id).first()
        
        # Verify portfolio exists
        assert retrieved_portfolio is not None
        assert retrieved_portfolio.id == portfolio.id
        
        # Verify position exists in portfolio
        assert len(retrieved_portfolio.positions) == 1
        retrieved_position = retrieved_portfolio.positions[0]
        
        # Verify all data is intact (round-trip)
        assert retrieved_position.id == original_id
        assert retrieved_position.ticker == original_ticker
        assert retrieved_position.quantity == original_quantity
        assert retrieved_position.purchase_price == original_price
        assert retrieved_position.purchase_date == original_date
        assert retrieved_position.portfolio_id == portfolio.id
    
    @given(
        user_data=user_data_strategy(),
        position_data_list=st.lists(stock_position_data_strategy(), min_size=2, max_size=5)
    )
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_5_multiple_positions_persistence(
        self,
        db_session: Session,
        user_data: dict,
        position_data_list: list
    ):
        """
        Test that multiple positions can be persisted and retrieved correctly.
        
        **Validates: Requirements 2.1, 7.2**
        """
        # Ensure clean session state
        db_session.rollback()
        
        # Create user and portfolio
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        
        portfolio = Portfolio(user_id=user.id)
        db_session.add(portfolio)
        db_session.commit()
        
        # Add multiple positions
        original_positions = []
        for position_data in position_data_list:
            position = StockPosition(
                portfolio_id=portfolio.id,
                **position_data
            )
            db_session.add(position)
            db_session.commit()
            db_session.refresh(position)
            original_positions.append({
                'id': position.id,
                'ticker': position.ticker,
                'quantity': position.quantity,
                'purchase_price': position.purchase_price,
                'purchase_date': position.purchase_date
            })
        
        # Clear session
        db_session.expire_all()
        
        # Retrieve portfolio
        retrieved_portfolio = db_session.query(Portfolio).filter_by(id=portfolio.id).first()
        
        # Verify all positions are present
        assert len(retrieved_portfolio.positions) == len(original_positions)
        
        # Verify each position's data
        retrieved_ids = {p.id for p in retrieved_portfolio.positions}
        original_ids = {p['id'] for p in original_positions}
        assert retrieved_ids == original_ids
        
        for original in original_positions:
            retrieved = next(p for p in retrieved_portfolio.positions if p.id == original['id'])
            assert retrieved.ticker == original['ticker']
            assert retrieved.quantity == original['quantity']
            assert retrieved.purchase_price == original['purchase_price']
            assert retrieved.purchase_date == original['purchase_date']


class TestConcurrentUpdates:
    """Test concurrent update consistency."""
    
    @given(
        user_data=user_data_strategy(),
        position_data=stock_position_data_strategy(),
        new_quantity=st.decimals(min_value=Decimal('0.0001'), max_value=Decimal('10000'), places=4)
    )
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_29_concurrent_update_consistency(
        self,
        db_session: Session,
        user_data: dict,
        position_data: dict,
        new_quantity: Decimal
    ):
        """
        **Property 29: Concurrent Update Consistency**
        
        For any portfolio being updated, the persistence layer should ensure 
        that all updates are applied atomically and the final state is consistent.
        
        Note: This test simulates sequential updates in a single session to verify
        consistency. True concurrent testing would require multiple database connections.
        
        **Validates: Requirements 7.3**
        """
        # Ensure clean session state
        db_session.rollback()
        
        # Create user, portfolio, and position
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        
        portfolio = Portfolio(user_id=user.id)
        db_session.add(portfolio)
        db_session.commit()
        
        position = StockPosition(
            portfolio_id=portfolio.id,
            **position_data
        )
        db_session.add(position)
        db_session.commit()
        db_session.refresh(position)
        
        original_id = position.id
        
        # Update the position
        position.quantity = new_quantity
        db_session.commit()
        
        # Clear session and retrieve
        db_session.expire_all()
        
        # Verify update was applied atomically
        retrieved_position = db_session.query(StockPosition).filter_by(id=original_id).first()
        assert retrieved_position is not None
        assert retrieved_position.quantity == new_quantity
        
        # Verify other fields remain unchanged
        assert retrieved_position.ticker == position_data['ticker']
        assert retrieved_position.purchase_price == position_data['purchase_price']
        assert retrieved_position.purchase_date == position_data['purchase_date']
    
    @given(
        user_data=user_data_strategy(),
        position_data=stock_position_data_strategy()
    )
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_29_transaction_rollback_on_error(
        self,
        db_session: Session,
        user_data: dict,
        position_data: dict
    ):
        """
        Test that failed updates are rolled back and don't leave inconsistent state.
        
        **Validates: Requirements 7.3**
        """
        # Ensure clean session state
        db_session.rollback()
        
        # Create user and portfolio
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        
        portfolio = Portfolio(user_id=user.id)
        db_session.add(portfolio)
        db_session.commit()
        
        position = StockPosition(
            portfolio_id=portfolio.id,
            **position_data
        )
        db_session.add(position)
        db_session.commit()
        
        original_quantity = position.quantity
        
        # Attempt to update with invalid data (negative quantity)
        try:
            position.quantity = Decimal('-1.0')
            db_session.commit()
            assert False, "Should have raised validation error"
        except ValueError:
            # Expected - validation should fail
            db_session.rollback()
        
        # Verify position still has original data
        db_session.refresh(position)
        assert position.quantity == original_quantity


class TestPersistenceRetry:
    """Test persistence retry logic."""
    
    @given(
        user_data=user_data_strategy(),
        position_data=stock_position_data_strategy()
    )
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_30_persistence_retry_logic(
        self,
        db_session: Session,
        user_data: dict,
        position_data: dict
    ):
        """
        **Property 30: Persistence Retry Logic**
        
        For any save operation that fails, the persistence layer should handle
        the error gracefully and maintain data integrity.
        
        Note: This test verifies error handling. Actual retry logic would be
        implemented at the service layer.
        
        **Validates: Requirements 7.4**
        """
        # Ensure clean session state
        db_session.rollback()
        
        # Create user and portfolio
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        portfolio = Portfolio(user_id=user.id)
        db_session.add(portfolio)
        db_session.commit()
        db_session.refresh(portfolio)
        
        # Attempt to create position with invalid ticker
        try:
            invalid_position = StockPosition(
                portfolio_id=portfolio.id,
                ticker="INVALID_TICKER_TOO_LONG",  # Too long
                quantity=position_data['quantity'],
                purchase_price=position_data['purchase_price'],
                purchase_date=position_data['purchase_date']
            )
            db_session.add(invalid_position)
            db_session.commit()
            assert False, "Should have raised validation error"
        except ValueError as e:
            # Expected - validation should fail
            db_session.rollback()
            assert "Invalid ticker format" in str(e)
        
        # Verify we can still create valid positions after error
        valid_position = StockPosition(
            portfolio_id=portfolio.id,
            **position_data
        )
        db_session.add(valid_position)
        db_session.commit()
        db_session.refresh(valid_position)
        
        # Verify the valid position was saved
        assert valid_position.id is not None
        assert valid_position.ticker == position_data['ticker']
    
    @given(
        user_data=user_data_strategy(),
        position_data=stock_position_data_strategy()
    )
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_30_cascade_delete_integrity(
        self,
        db_session: Session,
        user_data: dict,
        position_data: dict
    ):
        """
        Test that cascade deletes maintain referential integrity.
        
        **Validates: Requirements 7.4**
        """
        # Ensure clean session state
        db_session.rollback()
        
        # Create user, portfolio, and position
        user = User(**user_data)
        db_session.add(user)
        db_session.commit()
        
        portfolio = Portfolio(user_id=user.id)
        db_session.add(portfolio)
        db_session.commit()
        
        position = StockPosition(
            portfolio_id=portfolio.id,
            **position_data
        )
        db_session.add(position)
        db_session.commit()
        
        position_id = position.id
        portfolio_id = portfolio.id
        
        # Delete portfolio (should cascade to positions)
        db_session.delete(portfolio)
        db_session.commit()
        
        # Verify position was also deleted
        deleted_position = db_session.query(StockPosition).filter_by(id=position_id).first()
        assert deleted_position is None
        
        # Verify portfolio was deleted
        deleted_portfolio = db_session.query(Portfolio).filter_by(id=portfolio_id).first()
        assert deleted_portfolio is None
