from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config import get_settings

settings = get_settings()

# Configure database engine with SSL support
# For PostgreSQL, SSL mode can be configured via connection string or connect_args
engine_kwargs = {
    "pool_pre_ping": True,  # Verify connections before using them
    "pool_size": 10,
    "max_overflow": 20,
}

# Add SSL configuration for production databases
# SSL is enabled by default for most managed PostgreSQL services (AWS RDS, Google Cloud SQL, etc.)
# The connection string should include sslmode parameter for PostgreSQL
# Example: postgresql://user:pass@host/db?sslmode=require
if "postgresql" in settings.database_url and "sslmode" not in settings.database_url:
    # Add SSL requirement if not already specified
    separator = "&" if "?" in settings.database_url else "?"
    database_url = f"{settings.database_url}{separator}sslmode=prefer"
else:
    database_url = settings.database_url

engine = create_engine(database_url, **engine_kwargs)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
