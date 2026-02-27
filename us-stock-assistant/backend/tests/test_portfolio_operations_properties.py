"""
Property-based tests for portfolio operations.

Tests:
- Property 6: Invalid Ticker Rejection
"""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck, assume
from datetime import date, timedelta
from decimal import Decimal
import uuid
from sqlalchemy.orm import Session

from app.models import User, Portfolio
from app.services.portfolio_service import PortfolioService


# Custom strategies for generating test data
@st.composite
def invalid_ticker_strategy(draw):
    """Generate invalid ticker symbols."""
    # Choose one of several invalid patterns
    choice = draw(st.integers(min_value=0, max_value=4))
    
    if choice == 0:
        # Empty string or whitespace only
        return draw(st.sampled_from(["", "   ", "\t", "\n"]))
    elif choice == 1:
        # Too long (more than 10 characters)
        length = draw(st.integers(min_value=11, max_value=20))
        return ''.join(draw(st.lists(st.sampled_from('ABCDEFGHIJKLMNOPQRSTUVWXYZ'), min_size=length, max_size=length)))
    elif choice == 2:
        # Contains numbers (at least one digit)
        base = draw(st.text(alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ', min_size=0, max_size=4))
        digit = draw(st.sampled_from('0123456789'))
        return base + digit
    elif choice == 3:
        # Contains special characters
        return draw(st.text(alphabet='!@#$%^&*()', min_size=1, max_size=5))
    else:
        # Contains spaces (at least one space)
        parts = draw(st.lists(st.text(alphabet='ABCDEFGHIJKLMNOPQRSTUVWXYZ', min_size=1, max_size=3), min_size=2, max_size=2))
        return ' '.join(parts)


@st.composite
def valid_position_data_strategy(draw):
    """Generate valid stock position data (except ticker)."""
    quantity = draw(st.decimals(min_value=Decimal('0.0001'), max_value=Decimal('10000'), places=4))
    purchase_price = draw(st.decimals(min_value=Decimal('0.01'), max_value=Decimal('10000'), places=2))
    
    # Generate a date in the past (not future)
    days_ago = draw(st.integers(min_value=0, max_value=3650))  # Up to 10 years ago
    purchase_date = date.today() - timedelta(days=days_ago)
    
    return {
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


class TestInvalidTickerRejection:
    """Test that invalid ticker symbols are rejected."""
    
    @given(
        user_data=user_data_strategy(),
        invalid_ticker=invalid_ticker_strategy(),
        position_data=valid_position_data_strategy()
    )
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_6_invalid_ticker_rejection(
        self,
        db_session: Session,
        user_data: dict,
        invalid_ticker: str,
        position_data: dict
    ):
        """
        **Property 6: Invalid Ticker Rejection**
        
        For any invalid ticker symbol (empty string, special characters, 
        non-existent ticker), the portfolio service should reject the addition 
        and return an error.
        
        **Validates: Requirements 2.2**
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
        
        # Attempt to add position with invalid ticker
        with pytest.raises((ValueError, Exception)) as exc_info:
            portfolio_service.add_position(
                user_id=user.id,
                ticker=invalid_ticker,
                quantity=position_data['quantity'],
                purchase_price=position_data['purchase_price'],
                purchase_date=position_data['purchase_date']
            )
        
        # Verify error message indicates ticker validation failure
        error_message = str(exc_info.value).lower()
        assert any(keyword in error_message for keyword in ['ticker', 'invalid', 'format']), \
            f"Error message should mention ticker validation: {exc_info.value}"
        
        # Verify no position was created
        portfolio = portfolio_service.get_portfolio(user.id)
        if portfolio:
            assert len(portfolio.positions) == 0, "No position should be created with invalid ticker"
    
    @given(
        user_data=user_data_strategy(),
        invalid_ticker=invalid_ticker_strategy(),
        position_data=valid_position_data_strategy()
    )
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_6_invalid_ticker_no_side_effects(
        self,
        db_session: Session,
        user_data: dict,
        invalid_ticker: str,
        position_data: dict
    ):
        """
        Test that attempting to add an invalid ticker doesn't leave side effects.
        
        After a failed attempt with invalid ticker, valid operations should still work.
        
        **Validates: Requirements 2.2**
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
        
        # Attempt to add position with invalid ticker
        try:
            portfolio_service.add_position(
                user_id=user.id,
                ticker=invalid_ticker,
                quantity=position_data['quantity'],
                purchase_price=position_data['purchase_price'],
                purchase_date=position_data['purchase_date']
            )
            # If no exception, the ticker might have been valid by chance
            # (e.g., single letter like "A" is valid)
            # Skip this test case
            assume(False)
        except (ValueError, Exception):
            # Expected - invalid ticker should be rejected
            pass
        
        # Verify we can still add a valid position after the error
        valid_ticker = "AAPL"
        valid_position = portfolio_service.add_position(
            user_id=user.id,
            ticker=valid_ticker,
            quantity=position_data['quantity'],
            purchase_price=position_data['purchase_price'],
            purchase_date=position_data['purchase_date']
        )
        
        # Verify the valid position was created
        assert valid_position.id is not None
        assert valid_position.ticker == valid_ticker
        assert valid_position.quantity == position_data['quantity']
        
        # Verify portfolio has exactly one position
        portfolio = portfolio_service.get_portfolio(user.id)
        assert portfolio is not None
        assert len(portfolio.positions) == 1
        assert portfolio.positions[0].ticker == valid_ticker
    
    @given(
        user_data=user_data_strategy(),
        position_data=valid_position_data_strategy()
    )
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_6_whitespace_ticker_rejection(
        self,
        db_session: Session,
        user_data: dict,
        position_data: dict
    ):
        """
        Test that tickers with only whitespace are rejected.
        
        **Validates: Requirements 2.2**
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
        
        # Test various whitespace-only tickers
        whitespace_tickers = ["", "   ", "\t", "\n", " \t\n "]
        
        for whitespace_ticker in whitespace_tickers:
            with pytest.raises((ValueError, Exception)):
                portfolio_service.add_position(
                    user_id=user.id,
                    ticker=whitespace_ticker,
                    quantity=position_data['quantity'],
                    purchase_price=position_data['purchase_price'],
                    purchase_date=position_data['purchase_date']
                )
        
        # Verify no positions were created
        portfolio = portfolio_service.get_portfolio(user.id)
        if portfolio:
            assert len(portfolio.positions) == 0
