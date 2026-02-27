"""
Portfolio Service for managing user portfolios and stock positions.
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from decimal import Decimal
from datetime import date
import uuid

from app.models import Portfolio, StockPosition, User
from app.audit import log_portfolio_action, log_position_action


class PortfolioService:
    """Service for managing portfolios and stock positions."""
    
    def __init__(self, db: Session):
        """
        Initialize the portfolio service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    def create_portfolio(self, user_id: uuid.UUID) -> Portfolio:
        """
        Create a new portfolio for a user.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Created Portfolio object
            
        Raises:
            ValueError: If user doesn't exist or already has a portfolio
            SQLAlchemyError: If database operation fails
        """
        try:
            # Check if user exists
            user = self.db.query(User).filter(User.id == user_id).first()
            if not user:
                raise ValueError(f"User with id {user_id} not found")
            
            # Check if portfolio already exists
            existing_portfolio = self.db.query(Portfolio).filter(
                Portfolio.user_id == user_id
            ).first()
            if existing_portfolio:
                raise ValueError(f"Portfolio already exists for user {user_id}")
            
            # Create portfolio
            portfolio = Portfolio(user_id=user_id)
            self.db.add(portfolio)
            self.db.commit()
            self.db.refresh(portfolio)
            
            # Log action
            log_portfolio_action(
                db=self.db,
                action="create_portfolio",
                user_id=user_id,
                portfolio_id=str(portfolio.id),
                details={"portfolio_id": str(portfolio.id)}
            )
            
            return portfolio
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise
    
    def get_portfolio(self, user_id: uuid.UUID) -> Optional[Portfolio]:
        """
        Get a user's portfolio.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Portfolio object or None if not found
        """
        portfolio = self.db.query(Portfolio).filter(
            Portfolio.user_id == user_id
        ).first()
        return portfolio
    
    def add_position(
        self,
        user_id: uuid.UUID,
        ticker: str,
        quantity: Decimal,
        purchase_price: Decimal,
        purchase_date: date
    ) -> StockPosition:
        """
        Add a stock position to the user's portfolio.
        
        Args:
            user_id: ID of the user
            ticker: Stock ticker symbol
            quantity: Number of shares
            purchase_price: Price per share at purchase
            purchase_date: Date of purchase
            
        Returns:
            Created StockPosition object
            
        Raises:
            ValueError: If portfolio doesn't exist
            SQLAlchemyError: If database operation fails
        """
        try:
            # Get or create portfolio
            portfolio = self.get_portfolio(user_id)
            if not portfolio:
                portfolio = self.create_portfolio(user_id)
            
            # Create position
            position = StockPosition(
                portfolio_id=portfolio.id,
                ticker=ticker,  # Let the validator handle uppercase conversion
                quantity=quantity,
                purchase_price=purchase_price,
                purchase_date=purchase_date
            )
            
            self.db.add(position)
            self.db.commit()
            self.db.refresh(position)
            
            # Log action
            log_position_action(
                db=self.db,
                action="add_position",
                user_id=user_id,
                position_id=str(position.id),
                ticker=ticker,
                details={
                    "position_id": str(position.id),
                    "quantity": str(quantity),
                    "purchase_price": str(purchase_price),
                    "purchase_date": purchase_date.isoformat()
                }
            )
            
            return position
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise
    
    def update_position(
        self,
        user_id: uuid.UUID,
        position_id: uuid.UUID,
        quantity: Optional[Decimal] = None,
        purchase_price: Optional[Decimal] = None,
        purchase_date: Optional[date] = None
    ) -> StockPosition:
        """
        Update a stock position.
        
        Args:
            user_id: ID of the user
            position_id: ID of the position to update
            quantity: New quantity (optional)
            purchase_price: New purchase price (optional)
            purchase_date: New purchase date (optional)
            
        Returns:
            Updated StockPosition object
            
        Raises:
            ValueError: If position doesn't exist or doesn't belong to user
            SQLAlchemyError: If database operation fails
        """
        try:
            # Get position and verify ownership
            position = self.db.query(StockPosition).filter(
                StockPosition.id == position_id
            ).first()
            
            if not position:
                raise ValueError(f"Position with id {position_id} not found")
            
            # Verify user owns this position
            portfolio = self.db.query(Portfolio).filter(
                Portfolio.id == position.portfolio_id,
                Portfolio.user_id == user_id
            ).first()
            
            if not portfolio:
                raise ValueError(f"Position {position_id} does not belong to user {user_id}")
            
            # Track changes for audit log
            changes = {}
            
            # Update fields
            if quantity is not None:
                changes["quantity"] = {"old": str(position.quantity), "new": str(quantity)}
                position.quantity = quantity
            
            if purchase_price is not None:
                changes["purchase_price"] = {"old": str(position.purchase_price), "new": str(purchase_price)}
                position.purchase_price = purchase_price
            
            if purchase_date is not None:
                changes["purchase_date"] = {"old": position.purchase_date.isoformat(), "new": purchase_date.isoformat()}
                position.purchase_date = purchase_date
            
            self.db.commit()
            self.db.refresh(position)
            
            # Log action
            log_position_action(
                db=self.db,
                action="update_position",
                user_id=user_id,
                position_id=str(position.id),
                ticker=position.ticker,
                details={
                    "position_id": str(position.id),
                    "changes": changes
                }
            )
            
            return position
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise
    
    def remove_position(self, user_id: uuid.UUID, position_id: uuid.UUID) -> None:
        """
        Remove a stock position from the portfolio.
        
        Args:
            user_id: ID of the user
            position_id: ID of the position to remove
            
        Raises:
            ValueError: If position doesn't exist or doesn't belong to user
            SQLAlchemyError: If database operation fails
        """
        try:
            # Get position and verify ownership
            position = self.db.query(StockPosition).filter(
                StockPosition.id == position_id
            ).first()
            
            if not position:
                raise ValueError(f"Position with id {position_id} not found")
            
            # Verify user owns this position
            portfolio = self.db.query(Portfolio).filter(
                Portfolio.id == position.portfolio_id,
                Portfolio.user_id == user_id
            ).first()
            
            if not portfolio:
                raise ValueError(f"Position {position_id} does not belong to user {user_id}")
            
            # Store details for audit log before deletion
            position_details = {
                "position_id": str(position.id),
                "ticker": position.ticker,
                "quantity": str(position.quantity),
                "purchase_price": str(position.purchase_price),
                "purchase_date": position.purchase_date.isoformat()
            }
            
            # Delete position
            self.db.delete(position)
            self.db.commit()
            
            # Log action
            log_position_action(
                db=self.db,
                action="remove_position",
                user_id=user_id,
                position_id=str(position_id),
                ticker=position_details["ticker"],
                details=position_details
            )
            
        except SQLAlchemyError as e:
            self.db.rollback()
            raise

    async def calculate_metrics(
        self,
        user_id: uuid.UUID,
        stock_data_tools: Optional[any] = None
    ) -> dict:
        """
        Calculate portfolio metrics including total value, gain/loss, daily change, and diversity score.
        
        Args:
            user_id: ID of the user
            stock_data_tools: Optional StockDataMCPTools instance for fetching current prices
            
        Returns:
            Dictionary containing portfolio metrics:
                - total_value: Current total portfolio value
                - total_gain_loss: Total gain/loss in dollars
                - total_gain_loss_percent: Total gain/loss as percentage
                - daily_gain_loss: Daily change in dollars
                - diversity_score: Portfolio diversity score (0-1)
                - performance_by_period: Performance for different time periods
                
        Raises:
            ValueError: If portfolio doesn't exist
        """
        portfolio = self.get_portfolio(user_id)
        if not portfolio:
            # Auto-create empty portfolio for user
            portfolio = self.create_portfolio(user_id)
        
        if not portfolio.positions:
            # Empty portfolio
            return {
                "total_value": Decimal("0.00"),
                "total_gain_loss": Decimal("0.00"),
                "total_gain_loss_percent": Decimal("0.00"),
                "daily_gain_loss": Decimal("0.00"),
                "diversity_score": Decimal("0.00"),
                "performance_by_period": {
                    "1D": Decimal("0.00"),
                    "1W": Decimal("0.00"),
                    "1M": Decimal("0.00"),
                    "3M": Decimal("0.00"),
                    "1Y": Decimal("0.00"),
                    "ALL": Decimal("0.00")
                }
            }
        
        # Calculate total cost basis
        total_cost = sum(
            position.quantity * position.purchase_price
            for position in portfolio.positions
        )
        
        # If stock_data_tools provided, fetch current prices
        current_prices = {}
        if stock_data_tools:
            try:
                for position in portfolio.positions:
                    price_data = await stock_data_tools.get_stock_price(position.ticker)
                    current_prices[position.ticker] = {
                        "price": Decimal(str(price_data.price)),
                        "change": Decimal(str(price_data.change)),
                        "change_percent": Decimal(str(price_data.change_percent))
                    }
            except Exception as e:
                # If fetching prices fails, use purchase prices as fallback
                logger = __import__('logging').getLogger(__name__)
                logger.warning(f"Failed to fetch current prices: {e}")
                for position in portfolio.positions:
                    current_prices[position.ticker] = {
                        "price": position.purchase_price,
                        "change": Decimal("0.00"),
                        "change_percent": Decimal("0.00")
                    }
        else:
            # No stock data tools provided, use purchase prices
            for position in portfolio.positions:
                current_prices[position.ticker] = {
                    "price": position.purchase_price,
                    "change": Decimal("0.00"),
                    "change_percent": Decimal("0.00")
                }
        
        # Calculate total current value
        total_value = sum(
            position.quantity * current_prices[position.ticker]["price"]
            for position in portfolio.positions
        )
        
        # Calculate total gain/loss
        total_gain_loss = total_value - total_cost
        total_gain_loss_percent = (
            (total_gain_loss / total_cost * Decimal("100"))
            if total_cost > 0
            else Decimal("0.00")
        )
        
        # Calculate daily gain/loss
        daily_gain_loss = sum(
            position.quantity * current_prices[position.ticker]["change"]
            for position in portfolio.positions
        )
        
        # Calculate diversity score
        # Diversity score is based on:
        # 1. Number of different stocks (more is better)
        # 2. Even distribution of value across stocks (more even is better)
        
        num_positions = len(portfolio.positions)
        
        if num_positions == 1:
            diversity_score = Decimal("0.00")
        else:
            # Calculate value distribution
            position_values = [
                position.quantity * current_prices[position.ticker]["price"]
                for position in portfolio.positions
            ]
            
            # Calculate Herfindahl-Hirschman Index (HHI) for concentration
            # HHI ranges from 1/n (perfectly diversified) to 1 (concentrated)
            # We'll normalize it to 0-1 where 1 is perfectly diversified
            if total_value > 0:
                shares = [value / total_value for value in position_values]
                hhi = sum(share ** 2 for share in shares)
                
                # Normalize: perfect diversification (1/n) = 1.0, full concentration (1) = 0.0
                min_hhi = Decimal("1.0") / Decimal(str(num_positions))
                max_hhi = Decimal("1.0")
                
                if max_hhi > min_hhi:
                    diversity_score = (Decimal(str(hhi)) - max_hhi) / (min_hhi - max_hhi)
                    diversity_score = max(Decimal("0.00"), min(Decimal("1.00"), diversity_score))
                else:
                    diversity_score = Decimal("1.00")
            else:
                diversity_score = Decimal("0.00")
        
        # Calculate performance by period
        # Note: For now, we'll return placeholder values since we need historical data
        # This would require fetching historical prices for each position
        performance_by_period = {
            "1D": daily_gain_loss / total_cost * Decimal("100") if total_cost > 0 else Decimal("0.00"),
            "1W": Decimal("0.00"),  # Placeholder - needs historical data
            "1M": Decimal("0.00"),  # Placeholder - needs historical data
            "3M": Decimal("0.00"),  # Placeholder - needs historical data
            "1Y": Decimal("0.00"),  # Placeholder - needs historical data
            "ALL": total_gain_loss_percent
        }
        
        return {
            "total_value": total_value,
            "total_gain_loss": total_gain_loss,
            "total_gain_loss_percent": total_gain_loss_percent,
            "daily_gain_loss": daily_gain_loss,
            "diversity_score": diversity_score,
            "performance_by_period": performance_by_period
        }
    
    async def calculate_performance_by_period(
        self,
        user_id: uuid.UUID,
        stock_data_tools: any
    ) -> dict:
        """
        Calculate portfolio performance for multiple time periods.
        
        This method fetches historical data and calculates returns for:
        1D, 1W, 1M, 3M, 1Y, and ALL time periods.
        
        Args:
            user_id: ID of the user
            stock_data_tools: StockDataMCPTools instance for fetching historical data
            
        Returns:
            Dictionary with performance percentages for each period
            
        Raises:
            ValueError: If portfolio doesn't exist
        """
        from datetime import datetime, timedelta
        
        portfolio = self.get_portfolio(user_id)
        if not portfolio:
            raise ValueError(f"Portfolio not found for user {user_id}")
        
        if not portfolio.positions:
            return {
                "1D": Decimal("0.00"),
                "1W": Decimal("0.00"),
                "1M": Decimal("0.00"),
                "3M": Decimal("0.00"),
                "1Y": Decimal("0.00"),
                "ALL": Decimal("0.00")
            }
        
        # Define time periods
        today = date.today()
        periods = {
            "1D": today - timedelta(days=1),
            "1W": today - timedelta(weeks=1),
            "1M": today - timedelta(days=30),
            "3M": today - timedelta(days=90),
            "1Y": today - timedelta(days=365)
        }
        
        # Get current prices
        current_prices = {}
        for position in portfolio.positions:
            try:
                price_data = await stock_data_tools.get_stock_price(position.ticker)
                current_prices[position.ticker] = Decimal(str(price_data.price))
            except Exception:
                current_prices[position.ticker] = position.purchase_price
        
        # Calculate current total value
        current_total_value = sum(
            position.quantity * current_prices[position.ticker]
            for position in portfolio.positions
        )
        
        # Calculate performance for each period
        performance = {}
        
        for period_name, start_date in periods.items():
            try:
                # Get historical prices for each position at the start of the period
                period_start_value = Decimal("0.00")
                
                for position in portfolio.positions:
                    try:
                        historical_data = await stock_data_tools.get_historical_data(
                            ticker=position.ticker,
                            start_date=start_date,
                            end_date=start_date + timedelta(days=1)
                        )
                        
                        if historical_data:
                            # Use the close price from the historical data
                            historical_price = Decimal(str(historical_data[0].close))
                            period_start_value += position.quantity * historical_price
                        else:
                            # No historical data available, use current price
                            period_start_value += position.quantity * current_prices[position.ticker]
                    except Exception:
                        # If historical data fetch fails, use current price
                        period_start_value += position.quantity * current_prices[position.ticker]
                
                # Calculate percentage change
                if period_start_value > 0:
                    performance[period_name] = (
                        (current_total_value - period_start_value) / period_start_value * Decimal("100")
                    )
                else:
                    performance[period_name] = Decimal("0.00")
                    
            except Exception as e:
                # If calculation fails for this period, set to 0
                logger = __import__('logging').getLogger(__name__)
                logger.warning(f"Failed to calculate performance for {period_name}: {e}")
                performance[period_name] = Decimal("0.00")
        
        # Calculate ALL time performance (since purchase)
        total_cost = sum(
            position.quantity * position.purchase_price
            for position in portfolio.positions
        )
        
        if total_cost > 0:
            performance["ALL"] = (
                (current_total_value - total_cost) / total_cost * Decimal("100")
            )
        else:
            performance["ALL"] = Decimal("0.00")
        
        return performance

    def export_portfolio(
        self,
        user_id: uuid.UUID,
        format: str = "csv"
    ) -> bytes:
        """
        Export portfolio to CSV or Excel format.
        
        Args:
            user_id: ID of the user
            format: Export format ('csv' or 'excel')
            
        Returns:
            Bytes of the exported file
            
        Raises:
            ValueError: If portfolio doesn't exist or format is invalid
        """
        import pandas as pd
        from io import BytesIO
        
        portfolio = self.get_portfolio(user_id)
        if not portfolio:
            raise ValueError(f"Portfolio not found for user {user_id}")
        
        if format not in ('csv', 'excel'):
            raise ValueError(f"Invalid export format: {format}. Must be 'csv' or 'excel'")
        
        # Prepare data for export
        data = []
        for position in portfolio.positions:
            data.append({
                'ticker': position.ticker,
                'quantity': float(position.quantity),
                'purchase_price': float(position.purchase_price),
                'purchase_date': position.purchase_date.isoformat(),
                'position_id': str(position.id)
            })
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Export to requested format
        if format == 'csv':
            # Export to CSV with full precision
            buffer = BytesIO()
            df.to_csv(buffer, index=False, float_format='%.4f')
            buffer.seek(0)
            return buffer.getvalue()
        else:  # excel
            # Export to Excel with full precision
            buffer = BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Portfolio')
            buffer.seek(0)
            return buffer.getvalue()

    def import_portfolio(
        self,
        user_id: uuid.UUID,
        file_data: bytes,
        format: str = "csv"
    ) -> dict:
        """
        Import portfolio from CSV or Excel format.
        
        Args:
            user_id: ID of the user
            file_data: Bytes of the file to import
            format: Import format ('csv' or 'excel')
            
        Returns:
            Dictionary with import results:
                - success: Whether import was successful
                - imported_count: Number of positions imported
                - errors: List of error messages
                
        Raises:
            ValueError: If format is invalid
        """
        import pandas as pd
        from io import BytesIO
        
        if format not in ('csv', 'excel'):
            raise ValueError(f"Invalid import format: {format}. Must be 'csv' or 'excel'")
        
        errors = []
        imported_count = 0
        
        try:
            # Read file into DataFrame
            buffer = BytesIO(file_data)
            
            if format == 'csv':
                df = pd.read_csv(buffer)
            else:  # excel
                df = pd.read_excel(buffer, sheet_name='Portfolio')
            
            # Validate required columns
            required_columns = ['ticker', 'quantity', 'purchase_price', 'purchase_date']
            missing_columns = [col for col in required_columns if col not in df.columns]
            
            if missing_columns:
                errors.append(f"Missing required columns: {', '.join(missing_columns)}")
                return {
                    'success': False,
                    'imported_count': 0,
                    'errors': errors
                }
            
            # Import each row
            for index, row in df.iterrows():
                try:
                    # Validate and convert data
                    ticker = str(row['ticker']).strip()
                    quantity = Decimal(str(row['quantity']))
                    purchase_price = Decimal(str(row['purchase_price']))
                    
                    # Parse purchase date
                    if isinstance(row['purchase_date'], str):
                        purchase_date = date.fromisoformat(row['purchase_date'])
                    else:
                        # Handle pandas datetime
                        purchase_date = row['purchase_date'].date()
                    
                    # Add position
                    self.add_position(
                        user_id=user_id,
                        ticker=ticker,
                        quantity=quantity,
                        purchase_price=purchase_price,
                        purchase_date=purchase_date
                    )
                    
                    imported_count += 1
                    
                except Exception as e:
                    errors.append(f"Row {index + 1}: {str(e)}")
            
            # Log import action
            log_portfolio_action(
                db=self.db,
                action="import_portfolio",
                user_id=user_id,
                details={
                    'format': format,
                    'imported_count': imported_count,
                    'error_count': len(errors)
                }
            )
            
            return {
                'success': imported_count > 0,
                'imported_count': imported_count,
                'errors': errors
            }
            
        except Exception as e:
            errors.append(f"Failed to read file: {str(e)}")
            return {
                'success': False,
                'imported_count': 0,
                'errors': errors
            }
