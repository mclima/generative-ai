# Stock Agent 📈

An AI-powered US stock analysis dashboard that combines real-time market data with intelligent insights. Built with Next.js, FastAPI, LangChain, and OpenAI to demonstrate advanced agentic AI capabilities.

![Stock Agent](https://img.shields.io/badge/AI-Powered-blue)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![Python](https://img.shields.io/badge/Python-3.11+-blue)

## ✨ Features

### 🤖 Agentic AI Capabilities
- **OpenAI GPT-4o-mini Integration**: Intelligent stock analysis and insights generation
- **RAG (Retrieval-Augmented Generation)**: Context-aware analysis using ChromaDB vector store
- **Sentiment Analysis**: AI-powered news sentiment classification
- **Dynamic Insights**: Real-time bullish/bearish/neutral market signals
- **Free Tier Optimization**: Built with rate limiting and caching for cost-effective API usage

### 📊 Data Visualization
- **Interactive Charts**: Beautiful, responsive charts using Recharts
- **Real-time Stock Data**: Live quotes and metrics via Polygon.io API
- **Historical Analysis**: Comprehensive historical data tables
- **Multiple Timeframes**: 1D, 1W, 1M, 3M, 1Y, 5Y views

### 🎨 Modern UI/UX
- **Dark Theme**: Sleek black background with colorful accents
- **Responsive Design**: Mobile-first, works on all devices
- **Accessible**: WCAG compliant, keyboard navigation
- **SEO Optimized**: Meta tags, Open Graph, semantic HTML

### 📰 News Integration
- **Latest Market News**: Real-time news from multiple sources
- **AI Sentiment Analysis**: Automated positive/negative/neutral classification
- **Vector Storage**: News articles stored for contextual retrieval

## 🏗️ Architecture

```
stock-agent/
├── frontend/          # Next.js 14 + React + TypeScript
│   ├── src/
│   │   ├── app/       # App router pages
│   │   └── components/# React components
│   ├── tailwind.config.ts
│   └── package.json
│
└── backend/           # FastAPI + Python
    ├── services/      # Business logic
    │   ├── polygon_service.py    # Stock data API
    │   ├── openai_agent.py       # AI agent
    │   └── vector_store.py       # RAG implementation
    ├── routes/        # API endpoints
    ├── models/        # Pydantic models
    └── main.py        # FastAPI app
```

## 🚀 Tech Stack

### Frontend
- **Framework**: Next.js 14 (App Router)
- **UI Library**: React 18
- **Styling**: Tailwind CSS
- **Charts**: Recharts
- **Icons**: Lucide React
- **HTTP Client**: Axios
- **Language**: TypeScript

### Backend
- **Framework**: FastAPI
- **AI/ML**: LangChain, OpenAI GPT-4o-mini
- **Vector DB**: ChromaDB
- **Data Source**: Polygon.io API (Free Tier)
- **Language**: Python 3.11+

### Deployment
- **Frontend**: Vercel (optimized for Next.js)
- **Backend**: Railway (Python hosting)

## 📋 Prerequisites

- Node.js 18+ and npm/yarn
- Python 3.11+
- Polygon.io API key (Free tier: [Get one here](https://polygon.io/))
- OpenAI API key ([Get one here](https://platform.openai.com/))

### ⚠️ Free Tier Limitations
- **Polygon.io**: 5 API calls/minute, US stocks only
- **Rate Limit**: Search one stock per minute to avoid rate limits
- **Supported**: US stocks (NYSE, NASDAQ)
- **Not Supported**: Futures, options, crypto, international stocks

## 🛠️ Installation

See [SETUP.md](./SETUP.md) for detailed setup instructions.

## 🎯 Key Agentic Features

### 1. **Intelligent Analysis Agent**
The OpenAI agent analyzes multiple data sources:
- Current stock metrics (price, volume, P/E ratio)
- Historical performance (52-week range)
- Recent news articles
- Vector store context (RAG)

### 2. **RAG Implementation**
- News articles are embedded using OpenAI embeddings
- Stored in ChromaDB for semantic search
- Retrieved context enhances AI insights
- Persistent storage across sessions

### 3. **Multi-Step Reasoning**
The agent performs:
1. Data aggregation from multiple sources
2. Sentiment analysis on news
3. Context retrieval from vector store
4. Synthesis into actionable insights
5. Classification (bullish/bearish/neutral)

## 📊 API Endpoints

### Stock Data
- `GET /api/stock/{symbol}` - Get current stock data
- `GET /api/stock/{symbol}/chart` - Get chart data
- `GET /api/stock/{symbol}/historical` - Get historical data
- `GET /api/stock/{symbol}/news` - Get news with sentiment
- `GET /api/stock/{symbol}/insights` - Get AI insights

## 🎨 UI Components

- **StockSearch**: Symbol search with popular stocks
- **StockMetrics**: Real-time metrics display
- **StockChart**: Interactive price charts
- **AIInsights**: AI-generated analysis
- **NewsSection**: News feed with sentiment
- **StockTable**: Historical data table
- **InfoBanner**: Free tier limitations information
- **RateLimitAlert**: Dismissible rate limit warnings

## 🔒 Environment Variables

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### Backend (.env)
```
POLYGON_API_KEY=your_polygon_api_key
OPENAI_API_KEY=your_openai_api_key
ENVIRONMENT=development
PORT=8000
```

## 🚢 Deployment

### Frontend (Vercel)

#### Prerequisites
- GitHub account
- Vercel account (sign up at [vercel.com](https://vercel.com))
- Your backend API URL (Railway deployment URL)

#### Step-by-Step Deployment

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Vercel deployment"
   git push origin main
   ```

2. **Import to Vercel**
   - Go to [vercel.com/new](https://vercel.com/new)
   - Click "Import Project"
   - Select your GitHub repository
   - Choose the `stock-agent/frontend` directory as the root directory

3. **Configure Build Settings**
   - **Framework Preset**: Next.js (auto-detected)
   - **Root Directory**: `stock-agent/frontend`
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)
   - **Install Command**: `npm install` (default)

4. **Set Environment Variables**
   - Click "Environment Variables"
   - Add the following variable:
     ```
     NEXT_PUBLIC_API_URL=https://your-backend-url.railway.app
     ```
   - **Replace with your actual Railway URL** from Step 7 of the Backend deployment
   - Example: `NEXT_PUBLIC_API_URL=https://stock-agent-production.up.railway.app`
   - **Important**: Deploy your backend to Railway FIRST to get this URL

5. **Deploy**
   - Click "Deploy"
   - Wait 2-3 minutes for the build to complete
   - Your app will be live at `https://your-project-name.vercel.app`

6. **Configure Custom Domain (Optional)**
   - Go to Project Settings → Domains
   - Add your custom domain
   - Follow DNS configuration instructions

#### Post-Deployment

- **Automatic Deployments**: Every push to `main` branch will trigger a new deployment
- **Preview Deployments**: Pull requests automatically get preview URLs
- **Logs**: View build and runtime logs in the Vercel dashboard
- **Analytics**: Enable Vercel Analytics for performance insights

#### Troubleshooting

- **Build fails**: Check that `package.json` and `next.config.mjs` are in the frontend directory
- **API connection fails**: Verify `NEXT_PUBLIC_API_URL` is set correctly and backend is running
- **CORS errors**: Ensure your backend allows requests from your Vercel domain

### Backend (Railway)

#### Prerequisites
- GitHub account
- Railway account (sign up at [railway.app](https://railway.app))
- Polygon.io API key ([Get free tier](https://polygon.io/))
- OpenAI API key ([Get one here](https://platform.openai.com/))

#### Step-by-Step Deployment

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Railway deployment"
   git push origin main
   ```

2. **Create Railway Project**
   - Go to [railway.app/new](https://railway.app/new)
   - Click "Deploy from GitHub repo"
   - Authorize Railway to access your GitHub account
   - Select your `generative-ai` repository
   - Railway will scan for services

3. **Configure Service Settings**
   - **Root Directory**: Click "Settings" → "Service" → Set to `stock-agent/backend`
   - Railway will auto-detect Python using `nixpacks.toml` and `requirements.txt`
   - **Start Command**: Automatically configured via `nixpacks.toml`
   - If Railway doesn't auto-detect, manually set:
     - **Build Command**: `pip install -r requirements.txt`
     - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`

4. **Set Environment Variables**
   - In your Railway project dashboard, go to the **Variables** tab
   - Click "New Variable" and add each of the following:
     ```
     POLYGON_API_KEY=your_actual_polygon_api_key
     OPENAI_API_KEY=your_actual_openai_api_key
     ENVIRONMENT=production
     PORT=8000
     ```
   - **Important**: Replace placeholder values with your actual API keys
   - Railway will automatically redeploy when you add variables

5. **Configure CORS (Important)**
   - After deployment, note your Railway URL (e.g., `https://your-app.railway.app`)
   - Update your backend CORS settings to allow your Vercel frontend domain
   - In `backend/main.py`, ensure CORS allows your Vercel domain

6. **Deploy**
   - Railway automatically deploys on first setup
   - Monitor the deployment logs in real-time
   - Deployment typically takes 2-5 minutes
   - Wait for the build to complete successfully

7. **Get Your Backend URL** ⭐
   - After successful deployment, go to **Settings** → **Networking** (or **Domains**)
   - If no public domain exists, click **Generate Domain** to create one
   - Railway will generate a public URL like:
     ```
     https://stock-agent-production.up.railway.app
     ```
   - **Copy this URL** - you'll need it for your Vercel frontend
   - Test your API by visiting: `https://your-railway-url.railway.app/docs`
   - You should see the FastAPI Swagger documentation

8. **Important: Save Your Backend URL**
   - You'll use this URL as `NEXT_PUBLIC_API_URL` in your Vercel frontend deployment
   - Example: `NEXT_PUBLIC_API_URL=https://stock-agent-production.up.railway.app`

#### Post-Deployment

- **Automatic Deployments**: Every push to `main` branch triggers a new deployment
- **Logs**: View real-time logs in the Railway dashboard
- **Metrics**: Monitor CPU, memory, and network usage
- **Custom Domain**: Add your own domain in Settings → Domains
- **Scaling**: Railway auto-scales based on traffic (paid plans)

#### Troubleshooting

- **"Railpack could not determine how to build the app"**:
  - Ensure `nixpacks.toml` and `requirements.txt` are in the `backend` directory
  - Verify the root directory is set to `stock-agent/backend` in Railway settings
  - Try manually setting the start command: `uvicorn main:app --host 0.0.0.0 --port $PORT`
  - Check that you've committed and pushed all files to GitHub

- **Build fails**: 
  - Check that `requirements.txt` is in the `backend` directory
  - Verify Python version compatibility (3.11+)
  - Check build logs for missing dependencies

- **App crashes on startup**:
  - Verify all environment variables are set correctly
  - Check that `PORT` variable is set to `8000`
  - Review runtime logs for error messages

- **API not responding**:
  - Ensure the start command is correct: `uvicorn main:app --host 0.0.0.0 --port $PORT`
  - Check that Railway assigned a public domain
  - Verify CORS settings allow requests from your frontend

- **ChromaDB persistence issues**:
  - Railway provides ephemeral storage by default
  - For persistent vector storage, consider adding a Railway volume
  - Or use a managed vector database service

#### Cost Considerations

- **Free Tier**: Railway offers $5/month free credit
- **Usage**: This backend typically uses ~$3-5/month on Railway
- **Monitoring**: Track usage in the Railway dashboard to avoid overages

## 📈 Portfolio Highlights

This project demonstrates:
- ✅ Full-stack development (Next.js + FastAPI)
- ✅ AI/ML integration (OpenAI, LangChain)
- ✅ RAG implementation (ChromaDB)
- ✅ Real-time data processing
- ✅ Modern UI/UX design
- ✅ RESTful API design
- ✅ Type safety (TypeScript, Pydantic)
- ✅ Production-ready deployment

## 🤝 Contributing

This is a portfolio project, but suggestions are welcome!

## 📄 License

MIT License - feel free to use this for learning and portfolio purposes.

## 👤 Author

**Maria Lima**
- Portfolio: [mariaclima.ai]
- GitHub: [@mclima](https://github.com/mclima)

## 🙏 Acknowledgments

- [Polygon.io](https://polygon.io/) for stock market data
- [OpenAI](https://openai.com/) for GPT-4o-mini API
- [Recharts](https://recharts.org/) for beautiful, composable charts
- [Vercel](https://vercel.com/) for Next.js hosting
- [Railway](https://railway.app/) for backend hosting
- [ChromaDB](https://www.trychroma.com/) for vector storage
