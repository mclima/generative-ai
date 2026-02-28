import os
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager

from app.middleware import AuthMiddleware, ErrorHandlerMiddleware, LoggingMiddleware
from app.security_middleware import HTTPSRedirectMiddleware, SecurityHeadersMiddleware, CSRFProtectionMiddleware
from app.routers import auth, portfolio, stocks, news_market, analysis, alerts, preferences, websocket, compliance, health, admin
from app.services.price_update_service import get_price_update_service
from app.services.data_deletion_service import get_data_deletion_service
from app.logging_config import setup_logging, get_logger
from app.config import get_settings
from app.monitoring import init_monitoring, metrics_endpoint, MetricsMiddleware

# Initialize settings
settings = get_settings()

# Setup logging
setup_logging(
    level=getattr(settings, "log_level", "INFO"),
    json_format=True,
    enable_sanitization=True
)

logger = get_logger(__name__)

# Initialize monitoring
environment = getattr(settings, "environment", "development")
init_monitoring(environment=environment)

# Initialize rate limiter
limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.
    
    Handles startup and shutdown events for background tasks.
    """
    # Startup: Start price update service and data deletion service
    logger.info("Starting application...")
    price_service = get_price_update_service()
    await price_service.start()
    logger.info("Price update service started")
    
    deletion_service = get_data_deletion_service()
    await deletion_service.start()
    logger.info("Data deletion service started")
    
    yield
    
    # Shutdown: Stop services
    logger.info("Shutting down application...")
    await price_service.stop()
    logger.info("Price update service stopped")
    
    await deletion_service.stop()
    logger.info("Data deletion service stopped")


app = FastAPI(
    title="US Stock Assistant API",
    version="1.0.0",
    lifespan=lifespan
)

# Add rate limiter to app state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS configuration
# Read allowed origins from environment variable, default to localhost for development
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:3000,https://localhost:3000").split(",")
cors_origins_list = [origin.strip() for origin in cors_origins]
logger.info(f"CORS Origins configured: {cors_origins_list}")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins_list,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "PATCH"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-ID", "X-CSRF-Token"],
)

# Add security middleware
app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(CSRFProtectionMiddleware)
app.add_middleware(HTTPSRedirectMiddleware, enforce_https=False)  # Set to True in production

# Add metrics middleware
app.add_middleware(MetricsMiddleware)

# Add custom middleware (order matters - last added runs first)
app.add_middleware(ErrorHandlerMiddleware)
app.add_middleware(LoggingMiddleware)
app.add_middleware(AuthMiddleware)

# Include routers
app.include_router(auth.router)
app.include_router(portfolio.router)
app.include_router(stocks.router)
app.include_router(news_market.router)
app.include_router(analysis.router)
app.include_router(alerts.router)
app.include_router(preferences.router)
app.include_router(compliance.router)
app.include_router(websocket.router)
app.include_router(health.router)
app.include_router(admin.router)

@app.get("/health")
@limiter.limit("100/minute")
async def health_check(request: Request):
    return {"status": "healthy"}

@app.get("/metrics")
async def metrics(request: Request):
    """Prometheus metrics endpoint."""
    return await metrics_endpoint(request)
