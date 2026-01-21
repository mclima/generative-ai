# Agentic Job Board

AI-powered job aggregation system using LangGraph multi-agent architecture.

## 🎯 Project Status

✅ **Completed Features:**
1. LangGraph multi-agent system
2. FastAPI REST API with job endpoints
3. PostgreSQL persistence with deduplication
4. API hardening and error handling
5. Next.js frontend dashboard
6. **Transparency Panel** - Real-time agent execution monitoring
7. **LLM Integration** - OpenAI GPT-4o-mini for AI features
8. **Resume Matcher** - AI-powered resume-to-job matching with file upload support (PDF, DOCX, TXT)

## 🏗️ Architecture

### Backend Structure
```
backend/
├── app/
│   ├── graph/
│   │   ├── state.py              # TypedDict state definitions
│   │   └── teams/
│   │       └── ingestion/        # Parallel ingestion agents
│   │           ├── usajobs_agent.py
│   │           ├── themuse_agent.py
│   │           └── company_agent.py
│   ├── agents/                   # Processing agents
│   │   ├── classifier.py
│   │   ├── validator.py
│   │   └── ranker.py
│   ├── llm/
│   │   └── config.py             # Multi-LLM configuration
│   ├── transparency/
│   │   └── tracer.py             # Agent execution tracing
│   ├── api/
│   │   ├── schemas.py
│   │   └── adapter.py
│   ├── graph.py                  # LangGraph pipeline
│   └── main.py                   # FastAPI application
├── db.py                         # Database models
├── repository.py                 # Data access layer
└── requirements.txt
```

### Frontend Structure
```
frontend/
├── app/
│   ├── page.tsx                  # Home page
│   ├── jobs/
│   │   └── page.tsx              # Job listings
│   └── transparency/
│       └── page.tsx              # Transparency panel
├── components/
│   ├── JobCard.tsx
│   └── TransparencyPanel.tsx
└── lib/
    └── api.ts                    # API client
```



## 🎯 Target Job Categories

### 🧠 AI / Data
- AI Engineer
- Machine Learning Engineer
- LLM Engineer
- Data Scientist
- Data Engineer
- MLOps Engineer

### 💻 Software Engineering
- Frontend Engineer (React / Next.js)
- Backend Engineer (Python / Node / Java)
- Full-Stack Engineer
- Software Engineer
- Platform Engineer

### ☁️ Infrastructure / Operations
- DevOps Engineer
- Cloud Engineer
- Site Reliability Engineer (SRE)
- Security Engineer

## 📡 Job Sources

### Active Sources
- **JSearch**: Global job search API via RapidAPI (currently rate-limited due to free tier) with HTML entity decoding
- **Jobicy**: Remote-first developer jobs with full descriptions and HTML entity decoding
- **Company Pages**: Vercel careers via Greenhouse job board with HTML entity decoding

### Removed Sources
- **Adzuna**: Removed from codebase
- **LinkedIn Job Search API**: Removed due to API authentication issues (403/429 errors)

### Notes
- All sources focus on remote tech positions
- Parallel ingestion for faster job collection
- Automatic deduplication across sources
- HTML entity decoding applied at ingestion time across all sources for clean job titles and company names (e.g., `–` instead of `&#8211;`, `&` instead of `&amp;`)

## 🏗️ LangGraph Multi-Agent Pipeline

### Overview
LangGraph orchestrates the multi-agent workflow for fetching, processing, classifying, validating, and ranking jobs from multiple sources.

**Implementation:** `backend/app/job_graph.py` (lines 229-246)

### Pipeline Nodes

The graph defines a sequential pipeline with these nodes:

1. **ingest** - Parallel job fetching from multiple sources (JSearch, Jobicy, Vercel)
2. **process** - Normalize raw job data into standardized format
3. **classify** - Categorize jobs by role (AI, data, frontend, backend, etc.)
4. **validate** - Filter out non-tech jobs
5. **rank** - Score jobs by relevance

### Graph Execution

The LangGraph pipeline is invoked in:
- `backend/app/main.py` - Background refresh (automatic every 3 hours, request-triggered)
- `backend/app/main.py` - Manual refresh endpoint (`POST /jobs/refresh`)

### Key LangGraph Features

- **StateGraph** - Manages state flow between agents
- **Parallel execution** - Multiple ingestion sources run concurrently
- **Sequential processing** - Each agent processes results from the previous step

### Data Flow

```
┌─────────────────────────────────────┐
│         LangGraph Manager           │
└──────────────┬──────────────────────┘
               │
┌──────────────▼──────────────────────┐
│     Ingestion Team (Parallel)       │
│  ┌────────────────────────────────┐ │
│  │ JSearch Agent                  │ │
│  │ Jobicy Agent                   │ │
│  │ Company Agent                  │ │
│  └────────────────────────────────┘ │
└──────────────┬──────────────────────┘
               │
               ▼ RawJob[]
┌──────────────────────────────────────┐
│      Process (Normalization)         │
│  Standardize job data format         │
└──────────────┬───────────────────────┘
               │
               ▼ NormalizedJob[]
┌──────────────────────────────────────┐
│      Classify (Role Detection)       │
│  Categorize by job type              │
└──────────────┬───────────────────────┘
               │
               ▼ ClassifiedJob[]
┌──────────────────────────────────────┐
│      Validate (Quality Filter)       │
│  Remove non-tech positions           │
└──────────────┬───────────────────────┘
               │
               ▼ ValidJob[]
┌──────────────────────────────────────┐
│         Rank (Scoring)               │
│  Score by relevance                  │
└──────────────┬───────────────────────┘
               │
               ▼ ScoredJob[]
┌──────────────────────────────────────┐
│      Save to PostgreSQL              │
│  Deduplication + persistence         │
└──────────────────────────────────────┘
```

The LangGraph architecture enables efficient coordination of job ingestion from multiple sources, processing through various AI-powered stages, and delivering clean, categorized results to the database.

## 🔍 API Examples

### Search Jobs
```bash
GET /jobs?role=frontend&remote=true&limit=10&sort_by=score
```

### View Transparency Traces
```bash
GET /transparency/traces
```

### Check LLM Configuration
```bash
GET /config/llm
```


## 🚀 Quick Start

See [`SETUP.md`](./SETUP.md) for detailed setup instructions.

### Backend
```bash
# Start PostgreSQL (required for database)
brew services start postgresql@14

# Setup backend
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env  # Configure your API keys

# Create database
createdb jobboard

# Start server
uvicorn app.main:app --reload
```

### Frontend
```bash
cd frontend
npm install
cp .env.local.example .env.local
npm run dev
```

### Database Management
```bash
# Clear database (useful for testing or removing stale data)
psql jobboard -c "TRUNCATE TABLE jobdb CASCADE;"

# Trigger manual refresh (fetches fresh jobs from all sources)
curl -X POST "http://localhost:8000/jobs/refresh?force=true"
```

## 📊 Features

### 1. Multi-Agent Architecture
- **Ingestion Team**: Parallel job fetching from JSearch, Jobicy, and Vercel (Company Pages)
- **Understanding Team**: LLM-powered job classification and extraction
- **Ranking Team**: Relevance scoring and prioritization
- **Publishing Team**: Deduplication and persistence

**Cost-Optimized Refresh Strategy:**
- ✅ **Request-triggered refresh** (no APScheduler) - saves API costs on Railway/production
- ✅ **3-hour refresh interval** - balances freshness with API usage
- ✅ **Per-source tracking** - only fetches from sources that need refresh (40-60% fewer API calls)
- ✅ **Redis caching** (15-min TTL) - reduces database queries by 80-90%
- ✅ **Zero cost when idle** - no background jobs, refreshes only happen when users visit the site

**How it works:** Jobs refresh automatically when someone visits `/jobs` AND 3 hours have passed since last refresh. No traffic = no API calls = no costs. See `PERFORMANCE.md` for details.

### 2. AI-Powered Resume Matcher
Match your resume with relevant jobs using advanced AI:
- **Multiple input methods**: Upload PDF/DOCX/TXT files or paste text directly
- **Smart role mapping**: Automatically maps AI/ML/NLP roles to job categories
- **Skill extraction**: LLM-powered extraction of technical skills and experience
- **Intelligent scoring**: Prioritizes primary roles and rewards skill matches
- **Match explanations**: Clear explanations for why jobs match your profile

Access at: `http://localhost:3000/match`

**Features:**
- Upload resume files (PDF, DOCX, TXT) or paste text
- ATS-compatible resume parsing
- Role prioritization (primary role gets higher weight)
- AI/ML specialist bonus scoring
- Top 20 matches with percentage scores
- Skill overlap highlighting

### 3. Transparency Panel
Real-time monitoring of agent execution:
- View all execution traces
- Monitor agent step duration and status
- Debug failures with detailed error messages
- Track jobs processed per execution

Access at: `http://localhost:3000/transparency`

### 4. LLM Configuration
Using OpenAI GPT-4o-mini for AI-powered features:

```env
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.3
OPENAI_API_KEY=sk-...
```

### 5. REST API
- `GET /jobs` - Search and filter jobs
- `POST /jobs/match` - Match resume text to jobs
- `POST /jobs/match/upload` - Match resume file to jobs
- `GET /transparency/traces` - View execution traces
- `GET /config/llm` - Get LLM configuration

API Docs: `http://localhost:8000/docs`

## 🗄️ Database Management

### Reset Jobs Table
To clear all jobs and start fresh:
```bash
psql jobboard -c "DROP TABLE IF EXISTS jobs CASCADE;"
```

### Drop and Recreate Database
```bash
dropdb jobboard
createdb jobboard
```

### Check Database Status
```bash
# List all databases
psql -l

# Connect to database
psql jobboard

# View tables
psql jobboard -c "\dt"

# Count jobs
psql jobboard -c "SELECT COUNT(*) FROM jobs;"

# View job sources and counts
curl -s http://127.0.0.1:8000/jobs?limit=150 | python3 -c "import sys, json; data = json.load(sys.stdin); print(f'Total jobs: {len(data)}'); sources = {}; [sources.update({job['source']: sources.get(job['source'], 0) + 1}) for job in data]; [print(f'{k}: {v}') for k, v in sorted(sources.items())]"
```

## 🔧 Configuration

### Environment Variables

**Backend** (`.env`):
```env
DATABASE_URL=postgresql://user:pass@localhost:5432/jobboard
LLM_MODEL=gpt-4o-mini
LLM_TEMPERATURE=0.3
OPENAI_API_KEY=sk-...
```

**Frontend** (`.env.local`):
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 🔌 MCP Integration

This project can be extended with Model Context Protocol (MCP) for:
- External AI assistant integration
- Multi-agent collaboration
- Cross-platform job data sharing

See [`docs/MCP_INTEGRATION.md`](./docs/MCP_INTEGRATION.md) for implementation guide.

## 📝 Documentation

- [`SETUP.md`](./SETUP.md) - Detailed setup and deployment guide
- [`docs/MCP_INTEGRATION.md`](./docs/MCP_INTEGRATION.md) - MCP integration guide

## 🎯 Roadmap

✅ Completed:
1. LangGraph agents
2. FastAPI /jobs API
3. PostgreSQL persistence
4. API hardening
5. Next.js dashboard
6. Transparency panel
7. LLM upgrade capability
8. AI-powered resume matching with file upload
9. Smart role mapping for AI/ML engineers
10. Multiple job source integrations

Future enhancements:
- Email notifications for new matches
- Advanced filtering and search
- Job application tracking
- Saved searches and job alerts
- Company insights and reviews

### REFERENCE
What's Running:
✅ Backend: http://127.0.0.1:8000
✅ Frontend: http://localhost:3000
✅ PostgreSQL: Running and connected
✅ API Documentation: http://127.0.0.1:8000/docs
Available Pages:
Home: http://localhost:3000
Jobs: http://localhost:3000/jobs (showing test data)
Transparency Panel: http://localhost:3000/transparency
What Was Completed:
✅ Agentic System Confirmed - LangGraph multi-agent architecture
✅ MCP Assessment - Documented integration guide
✅ All Code Issues Fixed - Import errors, missing files, schemas
✅ Transparency Panel - Backend API + Frontend UI
✅ LLM Integration - OpenAI GPT-4o-mini for AI features
✅ Documentation - README, SETUP.md, MCP guide

### TODO
- Add job application tracking
- Add email notifications for new matches
- Add advanced filtering and search
- Add saved searches and job alerts
- Add company insights and reviews
