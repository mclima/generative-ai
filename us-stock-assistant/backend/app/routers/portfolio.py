"""
Portfolio API endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request, UploadFile, File, Response
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import date
from decimal import Decimal
import uuid

from app.database import get_db
from app.services.portfolio_service import PortfolioService
from app.services.stock_data_service import StockDataService
from app.routers.stocks import get_stock_data_service
from app.dependencies import CurrentUser
from app.validators import validate_ticker, sanitize_string
from slowapi import Limiter
from slowapi.util import get_remote_address

router = APIRouter(prefix="/api/portfolio", tags=["portfolio"])
limiter = Limiter(key_func=get_remote_address)


# Pydantic models
class StockPositionInput(BaseModel):
    ticker: str = Field(..., min_length=1, max_length=10)
    quantity: float = Field(..., gt=0)
    purchase_price: float = Field(..., gt=0)
    purchase_date: date
    
    @field_validator('ticker')
    @classmethod
    def validate_ticker_field(cls, v):
        return validate_ticker(v)


class StockPositionUpdate(BaseModel):
    quantity: Optional[float] = Field(None, gt=0)
    purchase_price: Optional[float] = Field(None, gt=0)
    purchase_date: Optional[date] = None


class StockPositionResponse(BaseModel):
    id: str
    ticker: str
    quantity: float
    purchase_price: float
    purchase_date: date
    current_price: float
    current_value: float
    gain_loss: float
    gain_loss_percent: float
    created_at: str
    updated_at: str


class PortfolioResponse(BaseModel):
    id: str
    user_id: str
    positions: List[StockPositionResponse]
    total_value: float
    total_gain_loss: float
    total_gain_loss_percent: float
    created_at: str
    updated_at: str


class PortfolioMetricsResponse(BaseModel):
    total_value: float
    total_gain_loss: float
    total_gain_loss_percent: float
    daily_gain_loss: float
    diversity_score: float
    performance_by_period: dict


class ImportResultResponse(BaseModel):
    success: bool
    imported_count: int
    errors: List[str]


def get_portfolio_service(db: Session = Depends(get_db)) -> PortfolioService:
    """Dependency to get PortfolioService instance."""
    return PortfolioService(db)


@router.get("", response_model=PortfolioResponse)
@limiter.limit("60/minute")
async def get_portfolio(
    request: Request,
    current_user: CurrentUser,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """
    Get user's portfolio with all positions.
    
    Requires authentication.
    Rate limit: 60 requests per minute.
    """
    portfolio = portfolio_service.get_portfolio(current_user.id)
    
    if not portfolio:
        # Create portfolio if it doesn't exist
        portfolio = portfolio_service.create_portfolio(current_user.id)
    
    # Convert to response format
    positions = []
    for pos in portfolio.positions:
        positions.append({
            "id": str(pos.id),
            "ticker": pos.ticker,
            "quantity": float(pos.quantity),
            "purchase_price": float(pos.purchase_price),
            "purchase_date": pos.purchase_date,
            "current_price": 0.0,  # Will be populated by frontend via stock data service
            "current_value": 0.0,
            "gain_loss": 0.0,
            "gain_loss_percent": 0.0,
            "created_at": pos.created_at.isoformat(),
            "updated_at": pos.updated_at.isoformat()
        })
    
    return {
        "id": str(portfolio.id),
        "user_id": str(portfolio.user_id),
        "positions": positions,
        "total_value": 0.0,  # Will be calculated by frontend
        "total_gain_loss": 0.0,
        "total_gain_loss_percent": 0.0,
        "created_at": portfolio.created_at.isoformat(),
        "updated_at": portfolio.updated_at.isoformat()
    }


@router.post("/positions", response_model=StockPositionResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("30/minute")
async def add_position(
    request: Request,
    body: StockPositionInput,
    current_user: CurrentUser,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """
    Add a new stock position to the portfolio.
    
    Requires authentication.
    Rate limit: 30 requests per minute.
    """
    try:
        position = portfolio_service.add_position(
            user_id=current_user.id,
            ticker=body.ticker,
            quantity=Decimal(str(body.quantity)),
            purchase_price=Decimal(str(body.purchase_price)),
            purchase_date=body.purchase_date
        )
        
        return {
            "id": str(position.id),
            "ticker": position.ticker,
            "quantity": float(position.quantity),
            "purchase_price": float(position.purchase_price),
            "purchase_date": position.purchase_date,
            "current_price": 0.0,
            "current_value": 0.0,
            "gain_loss": 0.0,
            "gain_loss_percent": 0.0,
            "created_at": position.created_at.isoformat(),
            "updated_at": position.updated_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to add position: {str(e)}"
        )


@router.put("/positions/{position_id}", response_model=StockPositionResponse)
@limiter.limit("30/minute")
async def update_position(
    request: Request,
    position_id: str,
    body: StockPositionUpdate,
    current_user: CurrentUser,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """
    Update an existing stock position.
    
    Requires authentication.
    Rate limit: 30 requests per minute.
    """
    try:
        position_uuid = uuid.UUID(position_id)
        
        # Build updates dict
        updates = {}
        if body.quantity is not None:
            updates['quantity'] = Decimal(str(body.quantity))
        if body.purchase_price is not None:
            updates['purchase_price'] = Decimal(str(body.purchase_price))
        if body.purchase_date is not None:
            updates['purchase_date'] = body.purchase_date
        
        position = portfolio_service.update_position(
            user_id=current_user.id,
            position_id=position_uuid,
            **updates
        )
        
        return {
            "id": str(position.id),
            "ticker": position.ticker,
            "quantity": float(position.quantity),
            "purchase_price": float(position.purchase_price),
            "purchase_date": position.purchase_date,
            "current_price": 0.0,
            "current_value": 0.0,
            "gain_loss": 0.0,
            "gain_loss_percent": 0.0,
            "created_at": position.created_at.isoformat(),
            "updated_at": position.updated_at.isoformat()
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position not found"
        )


@router.delete("/positions/{position_id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("30/minute")
async def remove_position(
    request: Request,
    position_id: str,
    current_user: CurrentUser,
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """
    Remove a stock position from the portfolio.
    
    Requires authentication.
    Rate limit: 30 requests per minute.
    """
    try:
        position_uuid = uuid.UUID(position_id)
        portfolio_service.remove_position(current_user.id, position_uuid)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Position not found"
        )


@router.get("/metrics", response_model=PortfolioMetricsResponse)
@limiter.limit("60/minute")
async def get_portfolio_metrics(
    request: Request,
    current_user: CurrentUser,
    stock_service: StockDataService = Depends(get_stock_data_service),
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """
    Get portfolio performance metrics.
    
    Requires authentication.
    Rate limit: 60 requests per minute.
    """
    try:
        metrics = await portfolio_service.calculate_metrics(current_user.id, stock_service.mcp_tools)
        return metrics
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/export")
@limiter.limit("10/minute")
async def export_portfolio(
    request: Request,
    current_user: CurrentUser,
    format: str = "csv",
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """
    Export portfolio data to CSV or Excel format.
    
    Requires authentication.
    Rate limit: 10 requests per minute.
    
    Query parameters:
    - format: "csv" or "excel" (default: "csv")
    """
    if format not in ["csv", "excel"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format must be 'csv' or 'excel'"
        )
    
    try:
        file_data = portfolio_service.export_portfolio(current_user.id, format)
        
        if format == "csv":
            media_type = "text/csv"
            filename = "portfolio.csv"
        else:
            media_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            filename = "portfolio.xlsx"
        
        return Response(
            content=file_data,
            media_type=media_type,
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/import", response_model=ImportResultResponse)
@limiter.limit("5/minute")
async def import_portfolio(
    request: Request,
    current_user: CurrentUser,
    file: UploadFile = File(...),
    format: str = "csv",
    portfolio_service: PortfolioService = Depends(get_portfolio_service)
):
    """
    Import portfolio data from CSV or Excel file.
    
    Requires authentication.
    Rate limit: 5 requests per minute.
    
    Query parameters:
    - format: "csv" or "excel" (default: "csv")
    """
    if format not in ["csv", "excel"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Format must be 'csv' or 'excel'"
        )
    
    try:
        file_data = await file.read()
        result = portfolio_service.import_portfolio(current_user.id, file_data, format)
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
