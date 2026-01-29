# Tech Job Board - Backend

Python FastAPI backend for the Tech Job Board application with AI-powered resume matching.

## Features

- Automated job aggregation from multiple sources (Jobicy, JSearch, Jobs API)
- Smart refresh strategy (scheduled refresh + manual refresh)
- AI-powered resume matching using Sentence Transformers (all-MiniLM-L6-v2) with pre-computed embeddings
- AI match explanations using OpenAI GPT-4o-mini for top 5 matches with 80%+ scores
- Sentence Transformer model pre-cached during deployment for instant resume matching
- Resume parsing (PDF, DOCX, TXT)
- RESTful API endpoints
- Direct PostgreSQL database operations with connection pooling
- Automatic job retention: Jobs older than 10 days are deleted, only jobs from last 10 days are displayed

## API Sources

The system uses a **two-phase refresh strategy** for optimal performance:

### Phase 1: Fast Refresh (initial API calls)

1. **Jobicy** (free) - 1 call
   - Fetches up to 50 remote tech jobs from USA
   
2. **JSearch** (RapidAPI) - 1 call
   - Query: "(software engineer OR software developer OR backend engineer OR frontend engineer OR full stack engineer OR data engineer OR data scientist OR machine learning engineer OR AI engineer OR generative AI OR LLM) in USA"
   - Note: May hit rate limits on free tier
   
3. **Jobs API** (RapidAPI) - up to 10 search calls
   - Query 1: "software engineer developer" (up to 5 pages)
   - Query 2: "AI machine learning engineer" (up to 5 pages)
   - Uses pagination with `nextToken` to fetch multiple pages
   - 1 second delay between calls to respect rate limits

**Initial call count:** 4 to 12 total

- Jobicy: 1
- JSearch: 1
- Jobs API search: 2 to 10 (depends on how many pages are available via pagination)

**Jobs appear immediately** with titles, companies, and locations. Descriptions show placeholder text.

### Phase 2: Background Description Loading (~30-60 calls, ~60-90 seconds)

After the fast refresh completes, a background task automatically fetches full job descriptions:
- **Detail calls:** ~30-60 calls (1 per Jobs API job)
- Runs silently in the background while users browse jobs
- Descriptions update in database as they're fetched
- No user wait time - happens automatically

**API Usage:**

- Initial refresh: 4 to 12 calls
- Background descriptions: 0 to N additional calls (roughly 1 per Jobs API job missing a full description)

All jobs are filtered for remote USA positions, posted within the last 10 days, and categorized based on comprehensive keyword matching. Jobs with title "AI/ML Developer" from DataAnnotation are automatically excluded.

## Setup

1. Create a virtual environment in the backend folder:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up PostgreSQL database:

**Option A: Using Homebrew (macOS)**
```bash
# Install PostgreSQL if not already installed
brew install postgresql@14

# Start PostgreSQL service
brew services start postgresql@14

# Verify PostgreSQL is running
brew services list | grep postgresql
```

**Option B: Using Docker**
```bash
docker run --name techjob-postgres \
  -e POSTGRES_USER=techjobuser \
  -e POSTGRES_PASSWORD=techjobpass \
  -e POSTGRES_DB=techjobboard \
  -p 5432:5432 \
  -d postgres:14
```

4. Create database user and database:
```bash
# Create the database user
psql postgres -c "CREATE USER techjobuser WITH PASSWORD 'techjobpass';"

# Create the database
psql postgres -c "CREATE DATABASE techjobboard OWNER techjobuser;"

# Grant privileges
psql postgres -c "GRANT ALL PRIVILEGES ON DATABASE techjobboard TO techjobuser;"
psql techjobboard -c "GRANT ALL ON SCHEMA public TO techjobuser;"

# Test the connection
psql -U techjobuser -d techjobboard -h localhost -c "SELECT version();"
```

5. Create `.env` file:
```bash
cp .env.example .env
```

6. Add your configuration to `.env`:
```
OPENAI_API_KEY=your_api_key_here
DATABASE_URL=postgresql://techjobuser:techjobpass@localhost:5432/techjobboard
ENVIRONMENT=development
```

**Note:** The database tables will be created automatically when you first run the application. The `init_db()` function in `app/database.py` creates the following tables:
- `jobs` - Stores job listings with fields like title, company, location, description, etc.
- `refresh_logs` - Tracks job refresh operations

7. Run the application:
```bash
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Deployment to Railway

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login to Railway:
```bash
railway login
```

3. Initialize project:
```bash
railway init
```

4. Add environment variables in Railway dashboard:
   - `OPENAI_API_KEY`
   - `DATABASE_URL` (Railway will provide PostgreSQL)

5. Deploy:
```bash
railway up
```

## API Endpoints

- `GET /api/jobs` - Get all jobs (with optional category and sort filters)
- `GET /api/jobs/{job_id}` - Get specific job details
- `POST /api/jobs/refresh` - Manually refresh job listings
- `POST /api/match-resume` - Match resume to jobs
- `GET /api/categories` - Get available job categories
- `GET /api/stats` - Get job statistics
