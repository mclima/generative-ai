# API Integration Guide

## Overview

NewsGenie integrates three external APIs to provide comprehensive news and information services.

---

## 1. OpenAI API (GPT-4o-mini)

### Purpose
- Query classification
- Response generation
- Natural language understanding

### Setup

1. **Get API Key**:
   - Visit [OpenAI Platform](https://platform.openai.com/api-keys)
   - Sign up or log in
   - Navigate to API Keys section
   - Click "Create new secret key"
   - Copy the key (starts with `sk-`)

2. **Add to .env**:
   ```
   OPENAI_API_KEY=sk-proj-xxxxxxxxxxxxx
   ```

3. **Pricing** (as of 2026):
   - GPT-4o-mini: ~$0.15 per 1M input tokens
   - GPT-4o-mini: ~$0.60 per 1M output tokens
   - Very cost-effective for this use case

### Usage in NewsGenie

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model="gpt-4o-mini",
    api_key=openai_api_key,
    temperature=0.7
)
```

**Functions**:
- `_classify_query()`: Determines query type and category
- `_generate_response()`: Creates natural language responses

---

## 2. GNews API

### Purpose
- Real-time news headlines
- Category-based news filtering
- News search functionality

### Setup

1. **Get API Key**:
   - Visit [GNews.io](https://gnews.io/)
   - Click "Get API Key" or "Sign Up"
   - Choose free tier (100 requests/day)
   - Copy your API key

2. **Add to .env**:
   ```
   GNEWS_API_KEY=your_gnews_api_key_here
   ```

3. **Free Tier Limits**:
   - 100 requests per day
   - Access to all categories
   - English language support
   - Up to 10 articles per request

### API Endpoints Used

#### Top Headlines
```
GET https://gnews.io/api/v4/top-headlines
Parameters:
  - category: technology, business, sports, etc.
  - lang: en
  - max: 5 (number of articles)
  - apikey: your_api_key
```

#### Search
```
GET https://gnews.io/api/v4/search
Parameters:
  - q: search query
  - lang: en
  - max: 5
  - apikey: your_api_key
```

### Response Format

```json
{
  "totalArticles": 5,
  "articles": [
    {
      "title": "Article Title",
      "description": "Article description...",
      "content": "Full content...",
      "url": "https://...",
      "image": "https://...",
      "publishedAt": "2026-01-22T10:30:00Z",
      "source": {
        "name": "Source Name",
        "url": "https://..."
      }
    }
  ]
}
```

### Categories Supported

- `general` - General news
- `world` - World news
- `nation` - National news
- `business` - Business/Finance
- `technology` - Technology
- `entertainment` - Entertainment
- `sports` - Sports
- `science` - Science
- `health` - Health

### Usage in NewsGenie

```python
from src.news_api import GNewsAPI

news_api = GNewsAPI(api_key=gnews_api_key)
result = news_api.fetch_top_headlines(category="technology", max_results=5)
```

### Error Handling

- **Rate Limit (429)**: Returns error message, suggests trying later
- **Timeout**: 10-second timeout with retry logic
- **Invalid Key**: Returns configuration error
- **No Results**: Returns empty articles array with success flag

---

## 3. Tavily API

### Purpose
- Web search for general queries
- Real-time information retrieval
- Context gathering for LLM responses

### Setup

1. **Get API Key**:
   - Visit [Tavily.com](https://tavily.com/)
   - Sign up for free account
   - Navigate to API section
   - Copy your API key (starts with `tvly-`)

2. **Add to .env**:
   ```
   TAVILY_API_KEY=tvly-xxxxxxxxxxxxx
   ```

3. **Free Tier**:
   - Check current limits on Tavily website
   - Sufficient for development and testing

### API Features

- **Search Depth**: Basic or advanced
- **Max Results**: Configurable (we use 3)
- **Answer Extraction**: AI-generated summary
- **Source Quality**: Ranked by relevance

### Usage in NewsGenie

```python
from src.web_search import WebSearchTool

search_tool = WebSearchTool(api_key=tavily_api_key)
result = search_tool.search(query="explain quantum computing", max_results=3)
```

### Response Format

```json
{
  "query": "explain quantum computing",
  "results": [
    {
      "title": "Result Title",
      "content": "Relevant content snippet...",
      "url": "https://...",
      "score": 0.95
    }
  ],
  "answer": "AI-generated summary of the topic..."
}
```

### Search Configuration

```python
response = client.search(
    query=query,
    max_results=3,
    search_depth="basic"  # or "advanced" for deeper search
)
```

---

## API Key Security

### Best Practices

1. **Never commit .env to git**:
   - Already in `.gitignore`
   - Use `.env.example` for templates

2. **Rotate keys regularly**:
   - Change keys every 3-6 months
   - Immediately rotate if exposed

3. **Use environment variables**:
   - Load with `python-dotenv`
   - Never hardcode in source files

4. **Limit key permissions**:
   - Use read-only keys when possible
   - Set usage limits on provider dashboards

### Loading Keys in Code

```python
import os
from dotenv import load_dotenv

load_dotenv()

openai_key = os.getenv("OPENAI_API_KEY")
gnews_key = os.getenv("GNEWS_API_KEY")
tavily_key = os.getenv("TAVILY_API_KEY")
```

---

## Rate Limiting Strategy

### Current Implementation

1. **Detection**:
   - Check HTTP status code 429
   - Parse error messages

2. **Response**:
   - Return user-friendly error message
   - Suggest trying again later
   - No automatic retries for rate limits

3. **Future Enhancements**:
   - Implement caching for news results
   - Add request queue with delays
   - Track daily usage

### Monitoring Usage

**GNews**:
- Check dashboard at gnews.io
- Monitor daily request count
- Upgrade if needed

**OpenAI**:
- View usage at platform.openai.com
- Set spending limits
- Monitor token consumption

**Tavily**:
- Check usage on Tavily dashboard
- Track search volume

---

## Troubleshooting

### Common Issues

1. **"API key not configured"**:
   - Verify `.env` file exists
   - Check key format (no quotes, spaces)
   - Ensure `load_dotenv()` is called

2. **"Rate limit exceeded"**:
   - Wait for rate limit reset (usually 24 hours)
   - Consider upgrading API tier
   - Implement caching

3. **"Request timeout"**:
   - Check internet connection
   - Verify API service status
   - Increase timeout duration if needed

4. **"Invalid API key"**:
   - Regenerate key on provider website
   - Update `.env` file
   - Restart application

### Testing API Keys

Run this test script:

```python
import os
from dotenv import load_dotenv
from src.news_api import GNewsAPI
from src.web_search import WebSearchTool
from langchain_openai import ChatOpenAI

load_dotenv()

# Test OpenAI
try:
    llm = ChatOpenAI(model="gpt-4o-mini", api_key=os.getenv("OPENAI_API_KEY"))
    llm.invoke("test")
    print("✅ OpenAI API key valid")
except:
    print("❌ OpenAI API key invalid")

# Test GNews
news_api = GNewsAPI()
result = news_api.fetch_top_headlines("general", 1)
if result["success"]:
    print("✅ GNews API key valid")
else:
    print(f"❌ GNews API key invalid: {result['error']}")

# Test Tavily
search = WebSearchTool()
result = search.search("test", 1)
if result["success"]:
    print("✅ Tavily API key valid")
else:
    print(f"❌ Tavily API key invalid: {result['error']}")
```

---

## Cost Estimation

### Monthly Usage (Moderate)

**Assumptions**:
- 100 queries per day
- Average 50 tokens per query
- 200 tokens per response

**OpenAI** (GPT-4o-mini):
- Input: 100 queries × 30 days × 50 tokens = 150K tokens
- Output: 100 queries × 30 days × 200 tokens = 600K tokens
- Cost: ~$0.02 + ~$0.36 = **~$0.38/month**

**GNews** (Free tier):
- 100 requests/day = sufficient for moderate use
- Cost: **$0/month** (free tier)

**Tavily** (Free tier):
- Check current pricing
- Estimated: **$0-5/month**

**Total Estimated Cost**: **~$0.38-5.38/month**

---

## API Documentation Links

- [OpenAI API Docs](https://platform.openai.com/docs)
- [GNews API Docs](https://gnews.io/docs/v4)
- [Tavily API Docs](https://docs.tavily.com/)

---

## Support

For API-specific issues:
- OpenAI: [help.openai.com](https://help.openai.com)
- GNews: Contact via website
- Tavily: Check documentation or support channels
