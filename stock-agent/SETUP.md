# Setup Guide 🚀

Complete setup instructions for the Stock Agent application.

## Table of Contents
1. [Prerequisites](#prerequisites)
2. [API Keys Setup](#api-keys-setup)
3. [Backend Setup](#backend-setup)
4. [Frontend Setup](#frontend-setup)
5. [Running Locally](#running-locally)
6. [Deployment](#deployment)
7. [Troubleshooting](#troubleshooting)

## Prerequisites

### Required Software
- **Node.js**: Version 18.x or higher
  ```bash
  node --version  # Should be v18.x or higher
  ```
- **Python**: Version 3.11 or higher
  ```bash
  python --version  # Should be 3.11.x or higher
  ```
- **npm** or **yarn**: Latest version
- **pip**: Python package manager

### Recommended Tools
- **Git**: For version control
- **VS Code**: With Python and TypeScript extensions
- **Postman**: For API testing

## API Keys Setup

### 1. Polygon.io API Key

1. Go to [polygon.io](https://polygon.io/)
2. Sign up for a free account
3. Navigate to Dashboard → API Keys
4. Copy your API key
5. **Free tier includes**: 5 API calls/minute, basic stock data

### 2. OpenAI API Key

1. Go to [platform.openai.com](https://platform.openai.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new secret key
5. Copy and save it securely (you won't see it again)
6. **Note**: GPT-4 access requires a paid account with credits

## Backend Setup

### 1. Navigate to Backend Directory
```bash
cd backend
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On macOS/Linux:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Configure Environment Variables
```bash
# Copy example env file
cp .env.example .env

# Edit .env file with your API keys
nano .env  # or use your preferred editor
```

Add your API keys:
```env
POLYGON_API_KEY=your_actual_polygon_api_key_here
OPENAI_API_KEY=your_actual_openai_api_key_here
ENVIRONMENT=development
PORT=8000
```

### 5. Verify Installation
```bash
python -c "import fastapi; import langchain; print('All imports successful!')"
```

## Frontend Setup

### 1. Navigate to Frontend Directory
```bash
cd frontend
```

### 2. Install Dependencies
```bash
# Using npm
npm install

# Or using yarn
yarn install
```

### 3. Configure Environment Variables
```bash
# Copy example env file
cp .env.local.example .env.local

# Edit .env.local
nano .env.local
```

Add your backend URL:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 4. Verify Installation
```bash
npm run build
```

## Running Locally

### Option 1: Run Both Services Separately

#### Terminal 1 - Backend
```bash
cd backend
source venv/bin/activate  # On Windows: venv\Scripts\activate
python main.py
```

Backend will run on: `http://localhost:8000`

#### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

Frontend will run on: `http://localhost:3000`

### Option 2: Using Process Managers

#### Using tmux (macOS/Linux)
```bash
# Create new session
tmux new -s stock-agent

# Split window
Ctrl+B then %

# In first pane - Backend
cd backend && source venv/bin/activate && python main.py

# Switch to second pane
Ctrl+B then arrow key

# In second pane - Frontend
cd frontend && npm run dev
```

### Testing the Application

1. **Open Browser**: Navigate to `http://localhost:3000`
2. **Test Search**: Enter a stock symbol (e.g., AAPL, TSLA)
3. **Check API**: Visit `http://localhost:8000/docs` for API documentation
4. **Verify Data**: Ensure charts, news, and AI insights load

## Deployment

### Frontend Deployment (Vercel)

#### 1. Prepare for Deployment
```bash
cd frontend
npm run build  # Verify build works
```

#### 2. Deploy to Vercel
```bash
# Install Vercel CLI
npm i -g vercel

# Login
vercel login

# Deploy
vercel
```

#### 3. Configure Environment Variables
In Vercel Dashboard:
1. Go to Project Settings → Environment Variables
2. Add: `NEXT_PUBLIC_API_URL` = `https://your-backend-url.railway.app`
3. Redeploy

### Backend Deployment (Railway)

#### 1. Prepare for Deployment
Create `railway.json` in backend directory:
```json
{
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

#### 2. Deploy to Railway
1. Go to [railway.app](https://railway.app/)
2. Sign in with GitHub
3. New Project → Deploy from GitHub repo
4. Select your repository
5. Choose `backend` directory

#### 3. Configure Environment Variables
In Railway Dashboard:
1. Go to Variables tab
2. Add all variables from `.env`:
   - `POLYGON_API_KEY`
   - `OPENAI_API_KEY`
   - `ENVIRONMENT=production`
3. Deploy

#### 4. Get Backend URL
- Copy the Railway-provided URL (e.g., `https://your-app.railway.app`)
- Update Vercel's `NEXT_PUBLIC_API_URL` with this URL

## Troubleshooting

### Backend Issues

#### Port Already in Use
```bash
# Find process using port 8000
lsof -i :8000

# Kill the process
kill -9 <PID>
```

#### Import Errors
```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Verify Python version
python --version  # Must be 3.11+
```

#### ChromaDB Errors
```bash
# Remove existing database
rm -rf chroma_db/

# Restart backend (will recreate)
python main.py
```

### Frontend Issues

#### Module Not Found
```bash
# Clear cache and reinstall
rm -rf node_modules package-lock.json
npm install
```

#### Build Errors
```bash
# Clear Next.js cache
rm -rf .next
npm run build
```

#### CORS Errors
Ensure backend has CORS middleware enabled (already configured in `main.py`)

### API Issues

#### Polygon.io Rate Limits
- Free tier: 5 calls/minute
- Solution: Wait 60 seconds between requests or upgrade plan

#### OpenAI API Errors
- Check API key is valid
- Ensure you have credits in your account
- Verify GPT-4 access (may need to upgrade)

### Common Error Messages

#### "No data found for symbol"
- Verify stock symbol is correct
- Check Polygon.io API key is valid
- Ensure symbol is traded on US markets

#### "Failed to fetch stock data"
- Check backend is running
- Verify API keys in `.env`
- Check network connectivity

## Development Tips

### Hot Reload
- Frontend: Automatically reloads on file changes
- Backend: Use `uvicorn main:app --reload` for auto-reload

### API Testing
```bash
# Test backend health
curl http://localhost:8000/health

# Test stock endpoint
curl http://localhost:8000/api/stock/AAPL
```

### Debugging

#### Backend Logs
```bash
# Run with verbose logging
python main.py --log-level debug
```

#### Frontend Logs
- Open browser DevTools (F12)
- Check Console tab for errors
- Check Network tab for API calls

## Next Steps

1. ✅ Verify both services are running
2. ✅ Test with different stock symbols
3. ✅ Check AI insights generation
4. ✅ Review news sentiment analysis
5. ✅ Deploy to production

## Support

If you encounter issues:
1. Check this troubleshooting guide
2. Review error messages carefully
3. Check API documentation:
   - [Polygon.io Docs](https://polygon.io/docs)
   - [OpenAI API Docs](https://platform.openai.com/docs)
   - [FastAPI Docs](https://fastapi.tiangolo.com/)
   - [Next.js Docs](https://nextjs.org/docs)

## Additional Resources

- [LangChain Documentation](https://python.langchain.com/)
- [ChromaDB Documentation](https://docs.trychroma.com/)
- [Recharts Documentation](https://recharts.org/)
- [Tailwind CSS Documentation](https://tailwindcss.com/)

---

**Happy Coding! 🚀**
