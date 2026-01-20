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
1. Push to GitHub
2. Import to Vercel
3. Set environment variables
4. Deploy

### Backend (Railway)
1. Push to GitHub
2. Create Railway project
3. Set environment variables
4. Deploy from GitHub

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
