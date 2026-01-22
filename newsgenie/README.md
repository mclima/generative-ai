# 🧞 NewsGenie - AI-Powered News & Information Assistant

NewsGenie is an intelligent assistant that combines real-time news updates with conversational AI to help you stay informed in today's fast-paced digital world.

## ✨ Features

- **Smart Query Classification**: Automatically distinguishes between news requests and general queries
- **Real-Time News**: Fetches latest headlines from multiple categories using GNews API
- **Web Search Integration**: Uses Tavily for comprehensive web searches
- **LangGraph Workflow**: Efficient query processing with state management
- **Interactive UI**: Beautiful Streamlit interface with chat functionality
- **Error Handling**: Robust fallback mechanisms for API failures

## 🏗️ Architecture

```
Frontend (Streamlit)
    ↓
LangGraph Workflow
    ├─→ Query Classifier
    ├─→ News Fetcher (GNews)
    ├─→ Web Search (Tavily)
    └─→ Response Generator (GPT-4o-mini)
```

## 📋 Prerequisites

- Python 3.9 or higher
- API Keys:
  - [OpenAI API Key](https://platform.openai.com/api-keys)
  - [GNews API Key](https://gnews.io/) (Free tier: 100 requests/day)
  - [Tavily API Key](https://tavily.com/) (Free tier available)

## 🚀 Installation

1. **Clone or navigate to the project directory**:
```bash
cd /Users/marialima/github/generative-ai/newsgenie
```

2. **Create a virtual environment**:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**:
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**:
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```
OPENAI_API_KEY=sk-...
GNEWS_API_KEY=...
TAVILY_API_KEY=tvly-...
```

## 🎯 Usage

1. **Start the application**:
```bash
streamlit run app.py
```

2. **Access the interface**:
   - Open your browser to `http://localhost:8501`
   - The app will automatically open in your default browser

3. **Try these queries**:
   - "What's the latest in technology?"
   - "Tell me about artificial intelligence"
   - "Sports news today"
   - "What's happening with the stock market?"

## 📁 Project Structure

```
newsgenie/
├── app.py                 # Streamlit UI application
├── src/
│   ├── __init__.py
│   ├── workflow.py        # LangGraph workflow orchestration
│   ├── news_api.py        # GNews API integration
│   └── web_search.py      # Tavily web search integration
├── static/
│   └── styles.css         # Application styles
├── docs/                  # Documentation files
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── .gitignore
└── README.md
```

## 🔧 Configuration

### News Categories
- Technology
- Finance/Business
- Sports
- General
- Health
- Science
- Entertainment

### API Rate Limits
- **GNews Free Tier**: 100 requests/day
- **Tavily Free Tier**: Check current limits on their website
- **OpenAI**: Based on your account tier

## 🛠️ How It Works

1. **Query Classification**: 
   - User input is analyzed by GPT-4o-mini
   - Classified as NEWS, GENERAL, or HYBRID
   - News category is extracted if applicable

2. **Data Fetching**:
   - NEWS queries → GNews API for latest headlines
   - GENERAL queries → Tavily web search
   - HYBRID queries → Both sources

3. **Response Generation**:
   - Context from news/web results is compiled
   - GPT-4o-mini generates a comprehensive response
   - Results are formatted and displayed

4. **Error Handling**:
   - API key validation at startup
   - Rate limit detection and user notification
   - Timeout handling with retry logic
   - Graceful degradation when services fail

## 🎨 UI Features

- **Sidebar**:
  - API configuration status
  - Quick news category selector
  - Clear chat history button
  - Example queries

- **Main Chat**:
  - Conversational interface
  - Real-time responses
  - Expandable news article cards
  - Source citations with links

## 📊 Sample Outputs

### Technology News
```
Latest AI Breakthrough Announced
Source: TechCrunch • 2026-01-22
Description: Major tech company unveils new AI model...
[Read more →]
```

### Finance News
```
Stock Market Reaches New High
Source: Bloomberg • 2026-01-22
Description: Markets surge following positive economic data...
[Read more →]
```

## 🔍 Troubleshooting

### API Keys Not Working
- Verify keys are correctly copied in `.env`
- Check API key validity on respective platforms
- Ensure no extra spaces or quotes

### No News Results
- Check GNews API rate limits
- Verify internet connection
- Try a different category

### Slow Responses
- Normal for first query (model initialization)
- Check your internet speed
- Consider upgrading API tiers for better performance

## 📝 Project Deliverables

This project demonstrates:

1. ✅ **AI Chatbot Design**: Query classification and conversation management
2. ✅ **Real-Time News Integration**: GNews API with multiple categories
3. ✅ **Workflow Management**: LangGraph-based orchestration
4. ✅ **Error Handling**: Comprehensive fallback mechanisms
5. ✅ **User Interface**: Interactive Streamlit application

## 🚧 Future Enhancements

- [ ] Add more news sources
- [ ] Implement news caching
- [ ] Add user preferences storage
- [ ] Multi-language support
- [ ] Export chat history
- [ ] News sentiment analysis
- [ ] Personalized news recommendations

## 📄 License

This project is created for educational purposes as part of an AI certification course.

## 🤝 Contributing

This is a course project, but suggestions are welcome!

## 📧 Support

For issues or questions, please refer to the course materials or contact your instructor.

---

Built with ❤️ using Streamlit, LangGraph, OpenAI GPT-4o-mini, GNews, and Tavily
