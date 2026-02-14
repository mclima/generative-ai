# AI Research Outline Generator

A multi-agent AI system that generates comprehensive research outlines using LangGraph, FastAPI, and Streamlit. The system orchestrates multiple specialized agents to search, scrape, analyze, and synthesize information into structured outlines.

## 🏗️ Architecture

```
Browser
  ↓
Streamlit (Frontend)
  ↓ HTTP
FastAPI (Backend)
  ↓
LangGraph (Multi-Agent Orchestration)
  ↓
Specialized Agents (Search → Scrape → Notes → Write → Edit)
  ↓
OpenAI API + Tavily Search
```

### Agent Workflow

**Process Type: Sequential**

The system uses a **sequential process** where each agent completes its task before the next one begins. There is no parallel execution, hierarchical supervision, or consensus-based decision making.

1. **Search Agent** - Finds relevant sources using Tavily
2. **Scraper Agent** - Extracts content from discovered URLs
3. **Note Taker** - Consolidates scraped content
4. **Writer Agent** - Creates structured outline with summaries (LLM Call)
5. **Editor Agent** - Polishes and refines the final output (LLM Call)

Each agent passes its output to the next agent in a linear chain: `search → scrape → notes → write → edit`

## 📁 Project Structure

```
research-assistant/
├── backend/
│   ├── main.py           # FastAPI server with logging
│   ├── llm.py            # OpenAI LLM configuration
│   ├── tools.py          # Search and scraping tools
│   ├── agents.py         # Agent definitions with error handling
│   ├── graph.py          # LangGraph workflow
│   ├── schemas.py        # Pydantic models
│   ├── fallback.py       # Fallback response generator with topic validation
│   ├── requirements.txt  # Python dependencies
│   └── .env              # API keys (not in repo)
│
├── frontend/
│   ├── app.py            # Streamlit UI
│   └── requirements.txt  # Frontend dependencies
│
└── railway.toml          # Deployment configuration
```

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- OpenAI API key
- Tavily API key

### Environment Setup

Create a `.env` file in the `backend/` directory:

```bash
OPENAI_API_KEY=your_openai_api_key_here
TAVILY_API_KEY=your_tavily_api_key_here
```

## 🖥️ Local Development

### 1. Start the Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8000
```

**Expected output:**
```
INFO:     Uvicorn running on http://0.0.0.0:8000
INFO:     Application startup complete.
```

### 2. Test the Backend (Optional)

```bash
curl -X POST http://0.0.0.0:8000/research \
  -H "Content-Type: application/json" \
  -d '{"topic":"carbon capture technologies"}'
```

### 3. Start the Frontend

Open a new terminal:

```bash
cd frontend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

source .venv/bin/activate
streamlit run app.py
```

**Expected output:**
```
Local URL: http://localhost:8501
```

## 📊 What to Observe

### Backend Terminal Logs

```
➡️ Starting LangGraph execution
✅ LangGraph completed
INFO: 127.0.0.1:59399 - "POST /research HTTP/1.1" 200 OK
```

### System Layers

| Layer                   | Runs Where         |
| ----------------------- | ------------------ |
| Streamlit UI            | Browser            |
| API Calls               | Frontend → Backend |
| LangGraph Orchestration | Backend Only       |
| LLM Calls               | Backend Only       |
| Tools (Tavily, Scraper) | Backend Only       |

## 🔧 Configuration

### Backend URL Configuration

The frontend needs to know where to find the backend API:

**Local Development:**
```python
# frontend/app.py - Update the backend URL to:
BACKEND_URL = "http://0.0.0.0:8000/research"
```

**Railway Deployment:**
```python
# frontend/app.py - Update the backend URL to:
BACKEND_URL = "http://backend:8000/research"
```

Railway uses internal networking, so `backend` resolves to your backend service automatically.

## 🎯 Features

- ✅ Multi-agent research workflow
- ✅ Real-time web search via Tavily
- ✅ Automatic content scraping
- ✅ Structured outline generation with summaries
- ✅ Clean Streamlit interface
- ✅ FastAPI backend with async support
- ✅ **Robust error handling with retry logic**
- ✅ **Topic validation to reject nonsensical queries**
- ✅ **Fallback mechanisms for failed agents**
- ✅ **Validation between pipeline steps**
- ✅ **User-friendly fallback responses with clickable search links**
- ✅ **Automatic environment variable loading with python-dotenv**

## 🛡️ Reliability Features

### Error Handling & Retry Logic

Each agent implements robust error handling:

- **Search Agent**: 3 retry attempts with exponential backoff
- **Scraper Agent**: Validates search results before scraping, skips gracefully if search failed
- **Writer Agent**: 2 retry attempts for LLM calls, fallback mode using general knowledge if no data
- **Editor Agent**: 2 retry attempts, returns unedited draft if editing fails

### Validation Between Steps

Agents check for errors from previous steps:
- Scraper validates search results before attempting to scrape
- Note taker checks for scraper errors
- Writer checks for missing notes and adapts accordingly
- Editor validates draft before editing

### Topic Validation

The system validates topics before processing to reject nonsensical queries:

**Invalid topics are rejected with helpful guidance:**
```markdown
## Invalid Research Topic

**Please provide a valid research topic.** Your query appears to contain random characters or is not a meaningful research question.

**Examples of valid topics:**
- "climate change effects on polar bears"
- "latest developments in quantum computing"
- "history of the Roman Empire"
- "benefits of Mediterranean diet"
```

### User-Friendly Fallback Responses

When the pipeline fails, users receive a helpful response with clickable search links:

**Fallback response includes:**
- Clear explanation of what went wrong
- Direct search links (Google News, Google Scholar, Wikipedia, etc.)
- Technical details for debugging
- Actionable next steps

**Example fallback:**
```markdown
## Research Assistant - Service Temporarily Limited

We encountered issues while researching "climate change effects".

### � Search Resources

- [Google News](https://news.google.com/search?q=climate+change+effects) - Latest news
- [Google Search](https://www.google.com/search?q=climate+change+effects) - General search
- [Wikipedia](https://en.wikipedia.org/wiki/Special:Search?search=climate+change+effects) - Encyclopedia
- [Google Scholar](https://scholar.google.com/scholar?q=climate+change+effects) - Academic papers

### 💡 What You Can Do

1. Try again in a few moments
2. Refine your topic
3. Use the links above
```

### Environment Variables

Environment variables are automatically loaded using `python-dotenv`:
- **Local development:** Reads from `.env` file
- **Railway deployment:** Uses Railway's environment variables

No manual export commands needed - just run `uvicorn main:app`

## 🚧 Future Enhancements

- [ ] LangSmith tracing integration
- [ ] Agent-level cost tracking
- [ ] Async job queues
- [ ] Docker containerization
- [ ] JWT authentication
- [ ] Rate limiting
- [ ] Caching layer

## 📝 API Endpoints

### POST `/research`

**Request:**
```json
{
  "topic": "carbon capture technologies"
}
```

**Response:**
```json
{
  "outline": "# Carbon Capture Technologies\n\n• Direct Air Capture\n  Summary of DAC technology...\n\n• Carbon Sequestration\n  Summary of sequestration methods..."
}
```

## 🛠️ Tech Stack

- **Backend:** FastAPI, LangGraph, LangChain
- **Frontend:** Streamlit
- **LLM:** OpenAI GPT-4o-mini
- **Search:** Tavily API
- **Deployment:** Railway (optional)

## 🚂 Railway Deployment

### Prerequisites

1. [Railway account](https://railway.app/)
2. GitHub repository with your code
3. OpenAI and Tavily API keys

### Deployment Steps

#### 1. Push to GitHub

```bash
git add .
git commit -m "Ready for Railway deployment"
git push origin main
```

#### 2. Create Backend Service

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Click **New Project** → **Deploy from GitHub repo**
3. Select your repository
4. Railway will auto-detect the backend service

**Configure Backend:**
- **Root Directory:** `backend`
- **Start Command:** `uvicorn main:app --host 0.0.0.0 --port $PORT`
- **Environment Variables:**
  ```
  OPENAI_API_KEY=your_openai_api_key
  TAVILY_API_KEY=your_tavily_api_key
  PORT=8000
  ```

#### 3. Create Frontend Service

1. In the same project, click **New Service** → **GitHub Repo**
2. Select the same repository

**Configure Frontend:**
- **Root Directory:** `frontend`
- **Start Command:** `streamlit run app.py --server.port $PORT --server.address 0.0.0.0`
- **Environment Variables:**
  ```
  BACKEND_URL=http://backend:8000
  PORT=8501
  ```

#### 4. Enable Private Networking

1. Go to backend service settings
2. Enable **Private Networking**
3. Note the internal URL (e.g., `backend.railway.internal`)
4. Update frontend's `BACKEND_URL` to: `http://backend:8000`

#### 5. Generate Domain

1. Go to frontend service settings
2. Click **Generate Domain**
3. Your app will be live at: `https://your-app.up.railway.app`

### Verify Deployment

Visit your Railway domain and test with a research topic. Check logs in Railway dashboard for any errors.

### Cost Estimation

- **Railway:** ~$5/month (Hobby plan)
- **OpenAI API:** Pay per use (~$0.01-0.10 per outline)
- **Tavily API:** Free tier available

### Testing

Manual testing guide available in `backend/test_manual.md`:

**Test scenarios:**
1. Invalid API key (search failure)
2. Invalid OpenAI key (writer failure)
3. Invalid topic validation
4. Network simulation

**To test:**
- Temporarily modify API keys in `.env`
- Restart backend and submit queries
- Observe fallback responses with helpful links



