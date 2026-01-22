# 🚀 NewsGenie Quick Start Guide

Get NewsGenie up and running in 5 minutes!

## Prerequisites

- Python 3.9 or higher installed
- Internet connection
- API keys (see below)

---

## Step 1: Get Your API Keys (5 minutes)

### OpenAI API Key
1. Go to [https://platform.openai.com/api-keys](https://platform.openai.com/api-keys)
2. Sign up or log in
3. Click "Create new secret key"
4. Copy the key (starts with `sk-`)

### GNews API Key
1. Go to [https://gnews.io/](https://gnews.io/)
2. Click "Get API Key" or "Sign Up"
3. Choose the free tier (100 requests/day)
4. Copy your API key

### Tavily API Key
1. Go to [https://tavily.com/](https://tavily.com/)
2. Sign up for a free account
3. Navigate to the API section
4. Copy your API key (starts with `tvly-`)

---

## Step 2: Installation

### Option A: Automated Setup (Recommended)

```bash
cd /Users/marialima/github/newsgenie
chmod +x setup.sh
./setup.sh
```

### Option B: Manual Setup

```bash
cd /Users/marialima/github/newsgenie

# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
```

---

## Step 3: Configure API Keys

Edit the `.env` file and add your API keys:

```bash
# Open .env in your favorite editor
nano .env  # or vim, code, etc.
```

Add your keys:

```
OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
GNEWS_API_KEY=your_gnews_key_here
TAVILY_API_KEY=tvly-xxxxxxxxxxxxx
```

Save and close the file.

---

## Step 4: Test Your Setup (Optional but Recommended)

```bash
python test_api.py
```

You should see:
```
✅ OpenAI API key is valid
✅ GNews API key is valid
✅ Tavily API key is valid
🎉 All API keys are configured!
```

---

## Step 5: Run NewsGenie!

```bash
streamlit run app.py
```

The app will automatically open in your browser at `http://localhost:8501`

---

## First Steps in the App

1. **Check the sidebar** - Verify all API keys are configured (green checkmark)

2. **Try a news query**:
   - Select a category (e.g., "Technology")
   - Click "Get Latest News"

3. **Try a general query**:
   - Type in the chat: "Explain quantum computing"
   - Press Enter

4. **Try a hybrid query**:
   - Type: "What's the latest AI news and explain neural networks"
   - See both news articles and explanations!

---

## Sample Queries to Try

### News Queries
- "What's the latest in technology?"
- "Show me sports news"
- "Finance news today"
- "Health headlines"

### General Queries
- "Explain artificial intelligence"
- "What is climate change?"
- "Tell me about quantum computing"
- "How does blockchain work?"

### Hybrid Queries
- "Latest Tesla news and explain electric vehicles"
- "What's happening with AI and explain machine learning"
- "Sports news and explain the rules of basketball"

---

## Troubleshooting

### "API keys not configured" error
- Make sure `.env` file exists in the project root
- Check that keys are on separate lines with no quotes
- Restart the app after editing `.env`

### "Rate limit exceeded" error
- GNews free tier: 100 requests/day
- Wait 24 hours or upgrade your plan
- Try a different query type

### App won't start
```bash
# Make sure virtual environment is activated
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt

# Try running again
streamlit run app.py
```

### Slow responses
- First query is slower (model initialization)
- Check your internet connection
- Normal response time: 2-5 seconds

---

## Project Structure

```
newsgenie/
├── app.py              # Main Streamlit application
├── src/
│   ├── workflow.py     # LangGraph workflow
│   ├── news_api.py     # GNews integration
│   └── web_search.py   # Tavily integration
├── static/
│   └── styles.css      # Application styles
├── docs/               # Documentation
├── .env                # Your API keys (not in git)
└── requirements.txt    # Python dependencies
```

---

## Next Steps

- Read the full [README.md](README.md) for detailed information
- Check [docs/API_GUIDE.md](docs/API_GUIDE.md) for API details
- Review [docs/WORKFLOW_DIAGRAM.md](docs/WORKFLOW_DIAGRAM.md) for architecture
- See [docs/SUBMISSION_GUIDE.md](docs/SUBMISSION_GUIDE.md) for project deliverables

---

## Getting Help

### Common Issues
- **Import errors**: Make sure virtual environment is activated
- **API errors**: Verify keys are correct in `.env`
- **Port in use**: Stop other Streamlit apps or use `--server.port 8502`

### Resources
- [Streamlit Documentation](https://docs.streamlit.io/)
- [LangChain Documentation](https://python.langchain.com/)
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)

---

## Stopping the App

Press `Ctrl+C` in the terminal where the app is running.

To deactivate the virtual environment:
```bash
deactivate
```

---

## Running Again Later

```bash
cd /Users/marialima/github/newsgenie
source venv/bin/activate
streamlit run app.py
```

---

**Enjoy using NewsGenie! 🧞**
