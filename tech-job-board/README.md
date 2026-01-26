# Tech Job Board - AI-Powered Remote Job Matching Platform

A full-stack web application that aggregates remote tech job listings in the United States and uses AI to match candidates with relevant opportunities based on their resumes.

## 🌟 Features

### Job Listings
- **Automated Aggregation**: Fetches jobs from multiple sources (Jobicy, JSearch, Jobs API)
- **Smart Categorization**: Categorization into AI and Engineering
- **Filtering & Sorting**: Browse by category and sort by date (newest/oldest)
- **Fresh Content**: Only shows jobs posted within the last 15 days
- **Remote-Only**: Exclusively US remote positions

### AI-Powered Resume Matching
- **Multi-Format Support**: Upload PDF, DOCX, or TXT files, or paste resume text
- **Enhanced Semantic Matching**: Uses Sentence Transformers (all-MiniLM-L6-v2) for intelligent matching
- **Hybrid Algorithm**:
  - Skill overlap (40%) - Technical skills matching
  - Semantic similarity (35%) - Transformer-based embeddings
  - Job title similarity (25%) - Role alignment
- **Minimum Match Threshold**: Only shows jobs with 60%+ match score
- **Color-Coded Results**:
  - 🟢 Green (80-100%): Strong Match
  - 🟠 Orange (60-79%): Moderate Match
- **Detailed Match Breakdown**: Each matched job shows:
  - Individual component scores (semantic, skills, title)
  - Matched skills from your resume
  - Score weights and calculations
- **Context-Aware**: Understands synonyms, context, and semantic relationships

### User Experience
- **Modern UI**: Dark theme with blue accents (#3b82f6)
- **Responsive Design**: Works on mobile, tablet, and desktop
- **Accessible**: ARIA labels and keyboard navigation
- **SEO-Friendly**: Optimized for search engines

## 🏗️ Architecture

### Backend (Python/FastAPI)
- **Framework**: FastAPI with async support
- **Database**: PostgreSQL with psycopg2 and connection pooling
- **AI/ML**: 
  - Sentence Transformers (all-MiniLM-L6-v2) for semantic matching
  - OpenAI GPT-4o-mini for resume analysis
  - scikit-learn for cosine similarity calculations
  - LangChain for AI orchestration
- **Job Aggregation**: Async HTTP requests to multiple job boards
- **Resume Parsing**: PyPDF2, python-docx for file processing

### Frontend (Next.js/React)
- **Framework**: Next.js 14 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **Date Formatting**: date-fns

## 📁 Project Structure

```
tech-job-board/
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   ├── config.py            # Configuration settings
│   │   ├── database.py          # Database setup
│   │   ├── models.py            # SQLAlchemy models
│   │   ├── schemas.py           # Pydantic schemas
│   │   ├── services.py          # Business logic
│   │   ├── job_aggregator.py   # Job fetching logic
│   │   ├── resume_matcher.py   # AI matching algorithm
│   │   └── resume_parser.py    # File parsing utilities
│   ├── requirements.txt
│   ├── .env.example
│   ├── railway.json             # Railway deployment config
│   └── README.md
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx       # Root layout
│   │   │   ├── page.tsx         # Home page
│   │   │   ├── jobs/[id]/       # Job details page
│   │   │   └── match-resume/    # Resume matching page
│   │   ├── components/
│   │   │   ├── Header.tsx
│   │   │   ├── JobCard.tsx
│   │   │   ├── MatchedJobCard.tsx
│   │   │   ├── CategoryTabs.tsx
│   │   │   └── SortDropdown.tsx
│   │   ├── lib/
│   │   │   ├── api.ts           # API client
│   │   │   └── utils.ts         # Helper functions
│   │   └── types/
│   │       └── index.ts         # TypeScript types
│   ├── package.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── vercel.json              # Vercel deployment config
│   └── README.md
└── docs/
    ├── prompt.md                # Original requirements
    └── matching-algorithm.md    # Algorithm documentation
```

## 🚀 Getting Started

### Prerequisites
- Python 3.9+
- Node.js 18+
- OpenAI API key

### Backend Setup

1. Navigate to backend directory:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up PostgreSQL:
```bash
# Install PostgreSQL if not already installed
# Create a database
createdb techjobboard
```

5. Create `.env` file:
```bash
cp .env.example .env
```

6. Add your configuration to `.env`:
```
OPENAI_API_KEY=your_api_key_here
DATABASE_URL=postgresql://user:password@localhost:5432/techjobboard
ENVIRONMENT=development
```

7. Run the server:
```bash
uvicorn app.main:app --reload
```

Backend will be available at `http://localhost:8000`

### Frontend Setup

1. Navigate to frontend directory:
```bash
cd frontend
```

2. Install dependencies:
```bash
npm install
```

3. Create `.env.local` file:
```bash
cp .env.local.example .env.local
```

4. Update API URL in `.env.local`:
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

5. Run the development server:
```bash
npm run dev
```

Frontend will be available at `http://localhost:3000`

## 📊 API Endpoints

### Jobs
- `GET /api/jobs` - Get all jobs (with optional category and sort filters)
- `GET /api/jobs/{job_id}` - Get specific job details
- `POST /api/jobs/refresh` - Manually refresh job listings
- `GET /api/last-refresh` - Get timestamp of last job refresh

### Resume Matching
- `POST /api/match-resume` - Match resume to jobs (multipart/form-data)

### Metadata
- `GET /api/categories` - Get available job categories
- `GET /api/stats` - Get job statistics

## 🔄 Job Refresh Strategy

Jobs synced daily via scheduled task to optimize API usage and provide instant search results.

The application implements a simple and efficient refresh strategy:

1. **Scheduled Daily Refresh**: Automated cron job runs at 3am EST daily to fetch fresh jobs
2. **Manual Refresh**: Users can manually trigger a refresh using the "Refresh Jobs" button
3. **Background Processing**: Job descriptions are fetched in the background for optimal performance
4. **Deduplication**: Only adds new jobs, prevents duplicates
5. **Last Refresh Display**: Shows when jobs were last updated on the main page

Jobs are refreshed **only** through the daily cron job or manual user action, ensuring predictable API usage and fresh content.

### Setting Up the Cron Job

To enable automated daily job refresh at 3am EST:

```bash
cd backend
chmod +x setup_cron.sh
./setup_cron.sh
```

This will display the cron job command. To install it:

```bash
(crontab -l 2>/dev/null; echo "0 8 * * * cd /path/to/tech-job-board/backend && /path/to/venv/bin/python app/cron_job.py >> /path/to/tech-job-board/backend/cron_job.log 2>&1") | crontab -
```

Note: Replace `/path/to/` with your actual project path. The cron job runs at 8am UTC (3am EST).

To remove the cron job later:
```bash
crontab -e  # then delete the line containing 'cron_job.py'
```

Note: Logs will be written to the `cron_job.log` file path you configure in your crontab entry.

## 🎯 Matching Algorithm

The resume matching algorithm uses a sophisticated hybrid approach with **Sentence Transformers**:

- **40%** - Skill overlap (Technical skills matching)
- **35%** - Semantic similarity (Sentence Transformers with all-MiniLM-L6-v2)
- **25%** - Job title similarity (Role alignment)

**Key Features:**
- Uses transformer-based embeddings for deep semantic understanding
- Captures context and relationships beyond keyword matching
- Understands synonyms and technical variations
- Pre-trained on 1+ billion sentence pairs

See [docs/matching-algorithm.md](docs/matching-algorithm.md) for detailed documentation.

## 🚢 Deployment

### Backend (Railway)

1. Install Railway CLI:
```bash
npm install -g @railway/cli
```

2. Login and initialize:
```bash
railway login
railway init
```

3. Set environment variables in Railway dashboard:
   - `OPENAI_API_KEY`
   - `DATABASE_URL` (Railway provides PostgreSQL)

4. Deploy:
```bash
railway up
```

### Frontend (Vercel)

1. Install Vercel CLI:
```bash
npm install -g vercel
```

2. Deploy:
```bash
vercel
```

3. Set environment variable in Vercel dashboard:
   - `NEXT_PUBLIC_API_URL` - Your Railway backend URL

## 🛠️ Technologies Used

### Backend
- FastAPI
- PostgreSQL with psycopg2
- Sentence Transformers (all-MiniLM-L6-v2)
- OpenAI GPT-4o-mini
- LangChain
- scikit-learn
- PyPDF2 & python-docx
- httpx & BeautifulSoup4

### Frontend
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Axios
- Lucide React
- date-fns

## 📝 Best Practices

### Security
- API keys stored in environment variables
- CORS configured for production
- Input validation on all endpoints
- Secure file upload handling

### Performance
- Async job fetching
- Database indexing on key fields
- Client-side caching
- Optimized TF-IDF calculations

### Code Quality
- Type safety with TypeScript and Pydantic
- Clean architecture with separation of concerns
- Comprehensive error handling
- RESTful API design

## 🤝 Contributing

This is a production-ready application built according to specific requirements. For modifications:

1. Follow existing code structure
2. Maintain type safety
3. Add tests for new features
4. Update documentation

## 📄 License

This project is built as a demonstration of AI-powered job matching technology.

## 🙏 Acknowledgments

- Job data sourced from Jobicy, JSearch (RapidAPI), and Jobs API (RapidAPI)
- AI powered by OpenAI GPT-4o-mini
- UI icons from Lucide React

---

Built with ❤️ using AI and modern web technologies
