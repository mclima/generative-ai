# US Stock Assistant

AI-powered portfolio management and stock analysis application.

## Architecture

- **Backend**: FastAPI (Python) with PostgreSQL and Redis
- **Frontend**: Next.js 14+ with TypeScript and Tailwind CSS
- **AI/Agents**: LangChain and LangGraph for agentic workflows
- **Data Access**: Model Context Protocol (MCP) for financial data

## Model Context Protocol (MCP) Integration

This project demonstrates integration with the **Model Context Protocol (MCP)**, an open standard from Anthropic for connecting AI systems to external data sources and tools.

### MCP Architecture

The application uses a hybrid approach to showcase both MCP protocol expertise and production pragmatism:

- **News Server**: Implements the official MCP protocol using the Python SDK (`mcp[cli]`)
  - Uses FastMCP framework for tool definitions
  - Runs over HTTP/SSE transport for cloud deployment
  - Demonstrates proper MCP tool implementation with type hints and docstrings
  - Location: `mcp-servers/news-server/server.py`

- **Stock Data & Market Data Servers**: Use simplified REST APIs
  - Pragmatic choice for production reliability
  - Easier deployment and debugging
  - Same functionality, simpler implementation

### Why This Hybrid Approach?

This architecture demonstrates:
1. **MCP Protocol Knowledge**: The news-server shows understanding of the official MCP standard
2. **Engineering Judgment**: Choosing REST for production services shows practical decision-making
3. **Flexibility**: Ability to work with both emerging standards and traditional APIs
4. **Production Focus**: Prioritizing reliability and maintainability

### MCP Tools Exposed

The news-server exposes three MCP tools:

- `get_stock_news(ticker, limit)` - Get news for specific stocks
- `get_market_news(limit)` - Get market-wide news
- `get_trending_tickers(limit)` - Get trending stocks by news volume

### Learn More

- [Model Context Protocol Specification](https://modelcontextprotocol.io)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [FastMCP Documentation](https://modelcontextprotocol.io/docs/develop/build-server)

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker and Docker Compose

### Setup

1. Start infrastructure services (redis, postgres):

```bash
docker compose up -d postgres redis
```

2. Set up backend:

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your configuration
alembic upgrade head
uvicorn app.main:app --reload
```

3. Set up MCP servers:

```bash
# News server (official MCP protocol)
cd mcp-servers/news-server
source venv/bin/activate
pip install -r requirements.txt
python server.py

# Stock data server (REST API)
cd mcp-servers/stock-data-server
source venv/bin/activate
pip install -r requirements.txt
python main.py

# Market data server (REST API)
cd mcp-servers/market-data-server
source venv/bin/activate
pip install -r requirements.txt
python main.py
```

See [mcp-servers/README.md](mcp-servers/README.md) for detailed setup instructions.

4. Set up frontend:

```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

### Access

- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── config.py          # Configuration management
│   │   ├── database.py        # Database connection
│   │   ├── models.py          # SQLAlchemy models
│   │   ├── main.py            # FastAPI application
│   │   └── redis_client.py    # Redis connection
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Backend tests
│   └── requirements.txt       # Python dependencies
├── frontend/
│   ├── app/                   # Next.js app directory
│   ├── components/            # React components
│   └── package.json           # Node dependencies
└── docker-compose.yml         # Local development services
```

## Database Schema

The application uses PostgreSQL with the following tables:

- `users` - User accounts and authentication
- `portfolios` - User portfolios
- `stock_positions` - Individual stock holdings
- `price_alerts` - Price alert configurations
- `user_preferences` - User settings and preferences
- `notifications` - In-app notifications
- `audit_log` - Audit trail for user actions

## Development

### Backend Development

Run tests:

```bash
cd backend
pytest
```

Create migration:

```bash
alembic revision --autogenerate -m "description"
```

### Frontend Development

Run linter:

```bash
cd frontend
npm run lint
```

Build for production:

```bash
npm run build
```

## Database Management

### View Database

```bash
docker exec -it stock_assistant_db psql -U postgres -d stock_assistant
# Common commands:
\dt              # List tables
\d users         # Describe users table
\q               # Quit
```

### Reset Database

```bash
cd backend
alembic downgrade base
alembic upgrade head
```

## Troubleshooting

### Backend Issues

**ModuleNotFoundError**: Ensure you're in the `backend` directory with virtual environment activated

**Database connection error**: Check PostgreSQL is running with `docker-compose ps` and verify `DATABASE_URL` in `.env`

**Redis connection error**: Ensure Redis is running with `docker-compose ps` and check `REDIS_URL` in `.env`

### Frontend Issues

**Cannot find module 'next'**: Run `npm install` in the frontend directory

**API errors**: Ensure backend is running on http://localhost:8000 and check `NEXT_PUBLIC_API_URL` in `.env.local`

### Docker Issues

**Port already allocated**: Stop other services using the same port or change port in `docker-compose.yml`

**Cannot connect to Docker daemon**: Ensure Docker Desktop is running

## Useful Commands

### Docker

```bash
docker-compose logs -f              # View all logs
docker-compose logs -f postgres     # View specific service logs
docker-compose restart              # Restart services
docker-compose down -v              # Stop and remove volumes
```

### Database Backup

```bash
# Backup
docker exec stock_assistant_db pg_dump -U postgres stock_assistant > backup.sql

# Restore
docker exec -i stock_assistant_db psql -U postgres stock_assistant < backup.sql
```

## Deployment

For production deployment instructions, see [DEPLOYMENT.md](DEPLOYMENT.md).

## License

MIT
