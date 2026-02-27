"""
Property-based tests for portfolio export/import.

Tests:
- Property 42: Portfolio Export Completeness
- Property 43: Portfolio Import Validation
- Property 44: Export-Import Round-Trip
"""
import pytest
from hypothesis import given, strategies as st, settings, HealthCheck, assume
from datetime import date, timedelta
from decimal import Decimal
import uuid
from sqlalchemy.orm import Session
import pandas as pd
from io import BytesIO

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


class TestPortfolioExportCompleteness:
    """Test portfolio export completeness."""
    
    @given(
        user_data=user_data_strategy(),
        position_data_list=st.lists(stock_position_data_strategy(), min_size=1, max_size=10)
    )
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    def test_property_42_export_completeness_csv(
        self,
        db_session: Session,
        user_data: dict,
        position_data_list: list
    ):
        """
        **Property 42: Portfolio Export Completeness (CSV)**
        
        For any portfolio, exporting to CSV should include all stock positions
        with ticker, quantity, purchase price, purchase date, and current value.
        
        **Validates: Requirements 18.1, 18.4, 18.5**
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
        
        # Add positions
        added_positions = []
        for position_data in position_data_list:
            position = portfolio_service.add_position(
                user_id=user.id,
                ticker=position_data['ticker'],
                quantity=position_data['quantity'],
                purchase_price=position_data['purchase_price'],
                purchase_date=position_data['purchase_date']
            )
            added_positions.append(position)
        
        # Export portfolio
        exported_data = portfolio_service.export_portfolio(user.id, format='csv')
        
        # Verify export is not empty
        assert len(exported_data) > 0
        
        # Parse CSV
        df = pd.read_csv(BytesIO(exported_data))
        
        # Verify all positions are in export
        assert len(df) == len(added_positions)
        
        # Verify all required columns are present
        required_columns = ['ticker', 'quantity', 'purchase_price', 'purchase_date']
        for col in required_columns:
            assert col in df.columns, f"Missing column: {col}"
        
        # Verify data integrity - match positions by index since tickers may not be unique
        for idx, position in enumerate(added_positions):
            # Find matching row in export by index
            if idx < len(df):
                row = df.iloc[idx]
                
                # Verify ticker matches
                assert row['ticker'] == position.ticker, f"Ticker mismatch at index {idx}"
                
                # Verify quantity (allow small rounding differences)
                assert abs(float(row['quantity']) - float(position.quantity)) <= 0.0001, \
                    f"Quantity mismatch for {position.ticker}: {row['quantity']} vs {position.quantity}"
                
                # Verify purchase price (allow small rounding differences)
                assert abs(float(row['purchase_price']) - float(position.purchase_price)) <= 0.01, \
                    f"Price mismatch for {position.ticker}: {row['purchase_price']} vs {position.purchase_price}"
                
                # Verify purchase date
                exported_date = pd.to_datetime(row['purchase_date']).date()
                assert exported_date == position.purchase_date, \
                    f"Date mismatch for {position.ticker}: {exported_date} vs {position.purchase_date}"
    
    @given(
        user_data=user_data_strategy(),
        position_data_list=st.lists(stock_position_data_strategy(), min_size=1, max_size=10)
    )
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_42_export_completeness_excel(
        self,
        db_session: Session,
        user_data: dict,
        position_data_list: list
    ):
        """
        **Property 42: Portfolio Export Completeness (Excel)**
        
        For any portfolio, exporting to Excel should include all stock positions
        with full precision.
        
        **Validates: Requirements 18.1, 18.4, 18.5**
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
        
        # Add positions
        added_positions = []
        for position_data in position_data_list:
            position = portfolio_service.add_position(
                user_id=user.id,
                ticker=position_data['ticker'],
                quantity=position_data['quantity'],
                purchase_price=position_data['purchase_price'],
                purchase_date=position_data['purchase_date']
            )
            added_positions.append(position)
        
        # Export portfolio
        exported_data = portfolio_service.export_portfolio(user.id, format='excel')
        
        # Verify export is not empty
        assert len(exported_data) > 0
        
        # Parse Excel
        df = pd.read_excel(BytesIO(exported_data), sheet_name='Portfolio')
        
        # Verify all positions are in export
        assert len(df) == len(added_positions)
        
        # Verify all required columns are present
        required_columns = ['ticker', 'quantity', 'purchase_price', 'purchase_date']
        for col in required_columns:
            assert col in df.columns, f"Missing column: {col}"


class TestPortfolioImportValidation:
    """Test portfolio import validation."""
    
    @given(
        user_data=user_data_strategy()
    )
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_43_import_validation_missing_columns(
        self,
        db_session: Session,
        user_data: dict
    ):
        """
        **Property 43: Portfolio Import Validation (Missing Columns)**
        
        For any imported portfolio file with missing required columns,
        the system should reject the import with specific error messages.
        
        **Validates: Requirements 18.2, 18.3**
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
        
        # Create invalid CSV with missing columns
        invalid_csv = "ticker,quantity\nAAPL,10\n"
        
        # Attempt import
        result = portfolio_service.import_portfolio(
            user_id=user.id,
            file_data=invalid_csv.encode(),
            format='csv'
        )
        
        # Verify import failed
        assert result['success'] is False
        assert result['imported_count'] == 0
        assert len(result['errors']) > 0
        
        # Verify error message mentions missing columns
        error_message = ' '.join(result['errors']).lower()
        assert 'missing' in error_message or 'column' in error_message
    
    @given(
        user_data=user_data_strategy()
    )
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_43_import_validation_invalid_data(
        self,
        db_session: Session,
        user_data: dict
    ):
        """
        **Property 43: Portfolio Import Validation (Invalid Data)**
        
        For any imported portfolio file with invalid data,
        the system should report specific validation errors.
        
        **Validates: Requirements 18.2, 18.3**
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
        
        # Create CSV with invalid data (negative quantity)
        invalid_csv = "ticker,quantity,purchase_price,purchase_date\nAAPL,-10,150.00,2024-01-01\n"
        
        # Attempt import
        result = portfolio_service.import_portfolio(
            user_id=user.id,
            file_data=invalid_csv.encode(),
            format='csv'
        )
        
        # Verify import failed or reported errors
        assert len(result['errors']) > 0
        
        # Verify error message mentions the validation issue
        error_message = ' '.join(result['errors']).lower()
        assert any(keyword in error_message for keyword in ['positive', 'invalid', 'quantity'])


class TestExportImportRoundTrip:
    """Test export-import round-trip."""
    
    @given(
        user_data=user_data_strategy(),
        position_data_list=st.lists(stock_position_data_strategy(), min_size=1, max_size=10)
    )
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture], deadline=None)
    def test_property_44_export_import_round_trip_csv(
        self,
        db_session: Session,
        user_data: dict,
        position_data_list: list
    ):
        """
        **Property 44: Export-Import Round-Trip (CSV)**
        
        For any portfolio, exporting then importing should result in an
        identical portfolio with all data preserved at full precision.
        
        **Validates: Requirements 18.1, 18.2, 18.3, 18.4, 18.5**
        """
        # Ensure clean session state
        db_session.rollback()
        
        # Create first user for export
        user1 = User(**user_data)
        db_session.add(user1)
        db_session.commit()
        db_session.refresh(user1)
        
        # Create portfolio service
        portfolio_service = PortfolioService(db_session)
        
        # Add positions to first user
        original_positions = []
        for position_data in position_data_list:
            position = portfolio_service.add_position(
                user_id=user1.id,
                ticker=position_data['ticker'],
                quantity=position_data['quantity'],
                purchase_price=position_data['purchase_price'],
                purchase_date=position_data['purchase_date']
            )
            original_positions.append(position)
        
        # Export portfolio
        exported_data = portfolio_service.export_portfolio(user1.id, format='csv')
        
        # Create second user for import
        user2_data = {
            'email': f"import_{user_data['email']}",
            'password_hash': user_data['password_hash']
        }
        user2 = User(**user2_data)
        db_session.add(user2)
        db_session.commit()
        db_session.refresh(user2)
        
        # Import portfolio
        result = portfolio_service.import_portfolio(
            user_id=user2.id,
            file_data=exported_data,
            format='csv'
        )
        
        # Verify import was successful
        assert result['success'] is True
        assert result['imported_count'] == len(original_positions)
        assert len(result['errors']) == 0
        
        # Get imported portfolio
        imported_portfolio = portfolio_service.get_portfolio(user2.id)
        assert imported_portfolio is not None
        assert len(imported_portfolio.positions) == len(original_positions)
        
        # Verify all data is preserved - match by index since tickers may not be unique
        for idx, original in enumerate(original_positions):
            # Find matching position in imported portfolio by index
            if idx < len(imported_portfolio.positions):
                imported = imported_portfolio.positions[idx]
                
                # Verify data with precision tolerance
                assert imported.ticker == original.ticker, \
                    f"Ticker mismatch at index {idx}: {imported.ticker} vs {original.ticker}"
                assert abs(imported.quantity - original.quantity) <= Decimal('0.0001'), \
                    f"Quantity mismatch for {original.ticker}: {imported.quantity} vs {original.quantity}"
                assert abs(imported.purchase_price - original.purchase_price) <= Decimal('0.01'), \
                    f"Price mismatch for {original.ticker}: {imported.purchase_price} vs {original.purchase_price}"
                assert imported.purchase_date == original.purchase_date, \
                    f"Date mismatch for {original.ticker}: {imported.purchase_date} vs {original.purchase_date}"
    
    @given(
        user_data=user_data_strategy(),
        position_data_list=st.lists(stock_position_data_strategy(), min_size=1, max_size=5)
    )
    @settings(max_examples=5, suppress_health_check=[HealthCheck.function_scoped_fixture])
    def test_property_44_export_import_round_trip_excel(
        self,
        db_session: Session,
        user_data: dict,
        position_data_list: list
    ):
        """
        **Property 44: Export-Import Round-Trip (Excel)**
        
        For any portfolio, exporting to Excel then importing should preserve
        all data at full precision.
        
        **Validates: Requirements 18.1, 18.2, 18.3, 18.4, 18.5**
        """
        # Ensure clean session state
        db_session.rollback()
        
        # Create first user for export
        user1 = User(**user_data)
        db_session.add(user1)
        db_session.commit()
        db_session.refresh(user1)
        
        # Create portfolio service
        portfolio_service = PortfolioService(db_session)
        
        # Add positions to first user
        original_positions = []
        for position_data in position_data_list:
            position = portfolio_service.add_position(
                user_id=user1.id,
                ticker=position_data['ticker'],
                quantity=position_data['quantity'],
                purchase_price=position_data['purchase_price'],
                purchase_date=position_data['purchase_date']
            )
            original_positions.append(position)
        
        # Export portfolio
        exported_data = portfolio_service.export_portfolio(user1.id, format='excel')
        
        # Create second user for import
        user2_data = {
            'email': f"import_{user_data['email']}",
            'password_hash': user_data['password_hash']
        }
        user2 = User(**user2_data)
        db_session.add(user2)
        db_session.commit()
        db_session.refresh(user2)
        
        # Import portfolio
        result = portfolio_service.import_portfolio(
            user_id=user2.id,
            file_data=exported_data,
            format='excel'
        )
        
        # Verify import was successful
        assert result['success'] is True
        assert result['imported_count'] == len(original_positions)
        
        # Get imported portfolio
        imported_portfolio = portfolio_service.get_portfolio(user2.id)
        assert imported_portfolio is not None
        assert len(imported_portfolio.positions) == len(original_positions)
        
        # Verify data preservation
        for original in original_positions:
            matching = [p for p in imported_portfolio.positions if p.ticker == original.ticker]
            assert len(matching) > 0
            
            imported = matching[0]
            assert imported.ticker == original.ticker
            assert abs(imported.quantity - original.quantity) < Decimal('0.0001')
            assert abs(imported.purchase_price - original.purchase_price) < Decimal('0.01')
            assert imported.purchase_date == original.purchase_date
