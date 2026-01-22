# NewsGenie Workflow Architecture

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                           USER INTERFACE                             │
│                         (Streamlit App)                              │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │   Sidebar    │  │  Chat Area   │  │   News Display Cards     │  │
│  │              │  │              │  │                          │  │
│  │ • Categories │  │ • Messages   │  │ • Title                  │  │
│  │ • Settings   │  │ • Input Box  │  │ • Description            │  │
│  │ • Clear Chat │  │ • History    │  │ • Source & Date          │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                │ User Query
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      LANGGRAPH WORKFLOW                              │
│                    (Orchestration Layer)                             │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                    STATE MANAGEMENT                            │  │
│  │  • messages: List[str]                                         │  │
│  │  • user_query: str                                             │  │
│  │  • query_type: str (NEWS/GENERAL/HYBRID)                       │  │
│  │  • news_category: Optional[str]                                │  │
│  │  • news_results: Optional[dict]                                │  │
│  │  • web_results: Optional[dict]                                 │  │
│  │  • final_response: str                                         │  │
│  │  • error: Optional[str]                                        │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                       │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │                     WORKFLOW NODES                             │  │
│  │                                                                 │  │
│  │  1. CLASSIFY_QUERY                                             │  │
│  │     ├─ Analyze user input with GPT-4o-mini                     │  │
│  │     ├─ Determine query type                                    │  │
│  │     └─ Extract news category if applicable                     │  │
│  │                                                                 │  │
│  │  2. FETCH_NEWS (if NEWS or HYBRID)                             │  │
│  │     ├─ Call GNews API                                          │  │
│  │     ├─ Parse articles                                          │  │
│  │     └─ Handle errors                                           │  │
│  │                                                                 │  │
│  │  3. WEB_SEARCH (if GENERAL or HYBRID)                          │  │
│  │     ├─ Call Tavily API                                         │  │
│  │     ├─ Extract relevant results                                │  │
│  │     └─ Handle errors                                           │  │
│  │                                                                 │  │
│  │  4. GENERATE_RESPONSE                                          │  │
│  │     ├─ Compile context from all sources                        │  │
│  │     ├─ Generate response with GPT-4o-mini                      │  │
│  │     └─ Format with citations                                   │  │
│  └───────────────────────────────────────────────────────────────┘  │
└───────────────────────────────┬─────────────────────────────────────┘
                                │
                                │ Results
                                ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      EXTERNAL SERVICES                               │
│                                                                       │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │   OpenAI     │  │    GNews     │  │        Tavily            │  │
│  │              │  │              │  │                          │  │
│  │ GPT-4o-mini  │  │ News API v4  │  │   Web Search API         │  │
│  │              │  │              │  │                          │  │
│  │ • Classify   │  │ • Headlines  │  │ • Search                 │  │
│  │ • Generate   │  │ • Categories │  │ • Extract                │  │
│  └──────────────┘  └──────────────┘  └──────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Detailed Workflow Flow

### 1. Query Classification Phase

```
User Input: "What's the latest in AI?"
     │
     ▼
┌─────────────────────────────────────┐
│   CLASSIFY_QUERY Node               │
│                                     │
│   System Prompt:                    │
│   "You are a query classifier..."   │
│                                     │
│   Analysis:                         │
│   • Keywords: "latest" → NEWS       │
│   • Topic: "AI" → technology        │
│                                     │
│   Output:                           │
│   TYPE: NEWS                        │
│   CATEGORY: technology              │
└─────────────────────────────────────┘
     │
     ▼
   Route Decision
```

### 2. Routing Logic

```
                    Query Type?
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ▼                ▼                ▼
    [NEWS]          [GENERAL]         [HYBRID]
        │                │                │
        │                │                │
        ▼                ▼                ▼
  Fetch News      Web Search      Fetch News
   (GNews)         (Tavily)       + Web Search
        │                │                │
        └────────────────┼────────────────┘
                         │
                         ▼
                Generate Response
                    (GPT-4o-mini)
```

### 3. News Fetching Phase

```
┌─────────────────────────────────────┐
│   FETCH_NEWS Node                   │
│                                     │
│   Input:                            │
│   • category: "technology"          │
│   • max_results: 5                  │
│                                     │
│   GNews API Call:                   │
│   GET /top-headlines                │
│   ?category=technology              │
│   &lang=en                          │
│   &max=5                            │
│   &apikey=***                       │
│                                     │
│   Response Processing:              │
│   • Parse JSON                      │
│   • Extract articles                │
│   • Format data                     │
│   • Handle errors                   │
│                                     │
│   Output:                           │
│   {                                 │
│     "success": true,                │
│     "articles": [...]               │
│   }                                 │
└─────────────────────────────────────┘
```

### 4. Web Search Phase

```
┌─────────────────────────────────────┐
│   WEB_SEARCH Node                   │
│                                     │
│   Input:                            │
│   • query: "explain AI"             │
│   • max_results: 3                  │
│                                     │
│   Tavily API Call:                  │
│   search(                           │
│     query="explain AI",             │
│     max_results=3,                  │
│     search_depth="basic"            │
│   )                                 │
│                                     │
│   Response Processing:              │
│   • Extract results                 │
│   • Get AI answer                   │
│   • Rank by score                   │
│   • Handle errors                   │
│                                     │
│   Output:                           │
│   {                                 │
│     "success": true,                │
│     "results": [...],               │
│     "answer": "..."                 │
│   }                                 │
└─────────────────────────────────────┘
```

### 5. Response Generation Phase

```
┌─────────────────────────────────────┐
│   GENERATE_RESPONSE Node            │
│                                     │
│   Context Assembly:                 │
│   ┌─────────────────────────────┐   │
│   │ === NEWS ARTICLES ===       │   │
│   │ 1. Article Title            │   │
│   │    Source: TechCrunch       │   │
│   │    Description...           │   │
│   │                             │   │
│   │ === WEB SEARCH RESULTS ===  │   │
│   │ 1. Result Title             │   │
│   │    Content snippet...       │   │
│   └─────────────────────────────┘   │
│                                     │
│   GPT-4o-mini Generation:           │
│   • Input: Context + User Query     │
│   • Process: Synthesize info        │
│   • Output: Natural language        │
│                                     │
│   Final Response:                   │
│   "Here are the latest AI news:     │
│    1. [Article summary]             │
│    2. [Article summary]             │
│    Sources: [links]"                │
└─────────────────────────────────────┘
```

---

## Error Handling Flow

```
                    API Call
                        │
                        ▼
                   Try Request
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ▼               ▼               ▼
    Success        Timeout          Error
        │               │               │
        │               ▼               ▼
        │          Retry 3x      Check Error Type
        │               │               │
        │               │        ┌──────┴──────┐
        │               │        │             │
        │               ▼        ▼             ▼
        │          Success?   Rate Limit   Other Error
        │               │        │             │
        └───────────────┼────────┘             │
                        │                      │
                        ▼                      ▼
                  Return Data          Return Error State
                        │                      │
                        └──────────┬───────────┘
                                   │
                                   ▼
                          Continue Workflow
                                   │
                                   ▼
                          Generate Response
                          (with available data)
```

---

## State Transitions

```
Initial State
    │
    ▼
┌─────────────────────┐
│ messages: []        │
│ user_query: "..."   │
│ query_type: ""      │
│ news_category: None │
│ news_results: None  │
│ web_results: None   │
│ final_response: ""  │
│ error: None         │
└─────────────────────┘
    │
    ▼ classify_query
┌─────────────────────┐
│ query_type: "NEWS"  │
│ news_category: "tech"│
└─────────────────────┘
    │
    ▼ fetch_news
┌─────────────────────┐
│ news_results: {...} │
└─────────────────────┘
    │
    ▼ generate_response
┌─────────────────────┐
│ final_response: "..."│
└─────────────────────┘
    │
    ▼
  END
```

---

## Parallel Processing (HYBRID Queries)

```
User Query: "Latest Tesla news and explain electric vehicles"
    │
    ▼
Classify: HYBRID
    │
    ├─────────────────┬─────────────────┐
    │                 │                 │
    ▼                 ▼                 │
Fetch News      Web Search             │
(Tesla news)    (EV explanation)       │
    │                 │                 │
    └─────────────────┴─────────────────┘
                      │
                      ▼
              Combine Results
                      │
                      ▼
            Generate Response
            (with both contexts)
```

---

## Session Management

```
User Session Start
    │
    ▼
Initialize st.session_state
    │
    ├─ messages: []
    ├─ workflow: None
    └─ api_keys_configured: False
    │
    ▼
Check API Keys
    │
    ├─ Load from .env
    ├─ Validate keys
    └─ Initialize workflow
    │
    ▼
Ready for Queries
    │
    ├─ User sends query
    ├─ Process through workflow
    ├─ Append to messages
    └─ Display response
    │
    ▼
Session Continues
(until user closes browser)
```

---

## Performance Optimization

### Caching Strategy (Future)

```
Query Received
    │
    ▼
Check Cache
    │
    ├─ Cache Hit?
    │   ├─ Yes → Return cached result
    │   └─ No → Continue to API
    │
    ▼
Fetch from API
    │
    ▼
Store in Cache
(with timestamp)
    │
    ▼
Return Result
```

### Cache Invalidation

- News cache: 15 minutes TTL
- Web search cache: 1 hour TTL
- Clear on category change
- Clear on explicit user request

---

## Monitoring Points

1. **Query Classification Accuracy**
   - Track correct vs incorrect classifications
   - Monitor edge cases

2. **API Response Times**
   - GNews: Target < 2s
   - Tavily: Target < 3s
   - OpenAI: Target < 2s

3. **Error Rates**
   - API failures
   - Timeout occurrences
   - Rate limit hits

4. **User Engagement**
   - Queries per session
   - Category preferences
   - Average session duration

---

## Future Enhancements

1. **Multi-Language Support**
   - Detect user language
   - Translate queries
   - Return localized news

2. **Personalization**
   - User preferences
   - Favorite categories
   - Reading history

3. **Advanced Features**
   - News summarization
   - Sentiment analysis
   - Trend detection
   - Email notifications

4. **Performance**
   - Redis caching
   - Async API calls
   - Response streaming
   - Load balancing
