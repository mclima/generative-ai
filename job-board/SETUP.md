# Agentic Job Board - Setup Guide

## Overview

This is an agentic job board system built with LangGraph, FastAPI, and Next.js. It uses multiple AI agents to ingest, understand, rank, and publish job listings from various sources.

## Architecture

### Backend (Python + LangGraph)
- **Multi-agent pipeline**: Ingestion → Understanding → Ranking → Publishing
- **Parallel ingestion**: USAJobs, TheMuse, Adzuna, Company Scraper agents
- **LLM-powered processing**: Configurable OpenAI or Anthropic models
- **PostgreSQL persistence**: Deduplication and efficient querying
- **Transparency tracing**: Full agent execution visibility

### Frontend (Next.js + React)
- **Job listings dashboard**: Browse and filter jobs
- **Transparency panel**: Monitor agent execution in real-time
- **Responsive UI**: Modern, clean interface

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL 14+
- OpenAI or Anthropic API key

## Backend Setup

### 1. Navigate to backend directory
```bash
cd backend
```

### 2. Create virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure environment variables
```bash
cp .env.example .env
```

Edit `.env` with your configuration:
```env
# Database
DATABASE_URL=postgresql://user:password@localhost:5432/jobboard

# LLM Provider (openai or anthropic)
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
LLM_TEMPERATURE=0.3

# API Keys
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here  # Optional

# Job Sources
ADZUNA_APP_ID=your_app_id
ADZUNA_API_KEY=your_key_here
```

### 5. Setup PostgreSQL database

#### Start PostgreSQL service (if not already running)
```bash
# Check if PostgreSQL is running
pg_isready

# If not running, start PostgreSQL (macOS with Homebrew)
brew services start postgresql@14

# Or restart if it's in an error state
brew services restart postgresql@14

# Wait a few seconds and verify it's running
pg_isready
```

#### Create the database (one-time setup)
```bash
# Create database
createdb jobboard

# Or using psql
psql -U postgres -c "CREATE DATABASE jobboard;"

# Verify database was created
psql -l
```

### 6. Run the backend
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

API Documentation: `http://localhost:8000/docs`

### 7. Job Refresh System

#### Automatic Daily Refresh
The system automatically refreshes jobs **once per day** on the first request after 24 hours. The refresh happens in the background, so the page loads instantly while new jobs are being fetched.

Check refresh status:
```bash
curl http://localhost:8000/jobs/refresh/status
```

#### Manual Refresh
To manually trigger a job refresh:

**Using curl:**
```bash
curl -X POST http://localhost:8000/jobs/refresh
```

**Using the API docs:**
Visit `http://localhost:8000/docs` and use the `/jobs/refresh` endpoint

#### Clear old jobs from database
```bash
# Clear all jobs
psql -d jobboard -c "DELETE FROM jobdb;"

#drop database
psql -d jobboard -c "DROP TABLE IF EXISTS jobdb CASCADE";

# Or clear jobs from specific sources
psql -d jobboard -c "DELETE FROM jobdb WHERE source NOT IN ('adzuna', 'jsearch', 'arbeitnow');"
```

**Note:** The system is configured to use only 3 fast API sources (Adzuna, JSearch, Arbeitnow) that provide complete job descriptions and salary information. Other sources are disabled but can be re-enabled in `backend/app/job_graph.py`.

## Frontend Setup

### 1. Navigate to frontend directory
```bash
cd frontend
```

### 2. Install dependencies
```bash
npm install
```

### 3. Configure environment
```bash
cp .env.local.example .env.local
```

Edit `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. Run the frontend
```bash
npm run dev
```

The frontend will be available at `http://localhost:3000`

## API Endpoints

### Jobs
- `GET /jobs` - List jobs with filtering and pagination
  - Query params: `role`, `remote`, `limit`, `offset`, `sort_by`, `order`

### Transparency
- `GET /transparency/traces` - List all execution traces
- `GET /transparency/traces/{trace_id}` - Get specific trace details

### Configuration
- `GET /config/llm` - Get current LLM configuration

## LLM Provider Configuration

### Using OpenAI (Default)
```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
OPENAI_API_KEY=sk-...
```

### Using Anthropic
```env
LLM_PROVIDER=anthropic
LLM_MODEL=claude-3-5-sonnet-20241022
ANTHROPIC_API_KEY=sk-ant-...
```

## Transparency Panel

The transparency panel provides real-time visibility into agent execution:

1. Navigate to `http://localhost:3000/transparency`
2. View all execution traces
3. Click on a trace to see detailed agent steps
4. Monitor duration, status, and errors for each agent

## Job Sources

### Configured Sources
- **USAJobs**: Government job listings
- **TheMuse**: Tech company jobs
- **Adzuna**: Aggregated job listings
- **Company Pages**: Direct scraping from Greenhouse/Lever

### Adding New Sources
1. Create new agent in `backend/app/graph/teams/ingestion/`
2. Implement ingestion function returning `RawJob[]`
3. Add to graph in `backend/app/graph.py`

## Development

### Backend Testing
```bash
cd backend
pytest
```

### Frontend Development
```bash
cd frontend
npm run dev
```

### Database Migrations
The system auto-creates tables on startup. For manual control:
```python
from db import create_tables
create_tables()
```

## Troubleshooting

### Database Connection Issues
- Verify PostgreSQL is running: `pg_isready`
- Check DATABASE_URL format: `postgresql://user:pass@host:port/db`
- Ensure database exists: `psql -l`

### API Key Issues
- Verify keys are set in `.env`
- Check key permissions and quotas
- Test with: `curl http://localhost:8000/config/llm`

### Frontend Not Connecting
- Ensure backend is running on port 8000
- Check CORS is enabled (already configured)
- Verify `NEXT_PUBLIC_API_URL` in `.env.local`

## Production Deployment

### Backend
- Use production WSGI server (Gunicorn)
- Set `DATABASE_URL` to production database
- Enable HTTPS
- Configure proper CORS origins

### Frontend
- Build: `npm run build`
- Deploy to Vercel/Netlify
- Set `NEXT_PUBLIC_API_URL` to production API

## MCP Integration (Optional)

This system can be extended with Model Context Protocol (MCP) to:
- Expose job search as a tool for external LLMs
- Provide job database as a resource
- Enable multi-agent collaboration

See `docs/MCP_INTEGRATION.md` for details.
