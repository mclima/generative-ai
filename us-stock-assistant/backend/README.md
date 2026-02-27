# US Stock Assistant Backend

FastAPI backend for the US Stock Assistant application.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Start PostgreSQL and Redis:

```bash
docker-compose up -d
```

3. Copy environment file:

```bash
cp .env.example .env
```

4. Run database migrations:

```bash
alembic upgrade head
```

5. Start the development server:

```bash
uvicorn app.main:app --reload
```

The API will be available at http://localhost:8000

## Database Migrations

Create a new migration:

```bash
alembic revision --autogenerate -m "description"
```

Apply migrations:

```bash
alembic upgrade head
```

Rollback migration:

```bash
alembic downgrade -1
```

https://github.com/modelcontextprotocol/servers
