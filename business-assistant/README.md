# Catalyst AI - AI-Powered Business Intelligence Assistant

An innovative Business Intelligence Assistant that leverages advanced AI technologies including LangChain, Retrieval-Augmented Generation (RAG), and Large Language Models (LLMs) to analyze business data and generate actionable insights.

## 🎯 Project Objectives

- **Analyze business data**: Perform comprehensive analysis to identify key trends and patterns
- **Generate insights and recommendations**: Utilize natural language processing to deliver actionable business insights
- **Visualize data insights**: Present insights through interactive visualizations for easier interpretation

## 🚀 Features

### Part 1: AI-Powered Business Intelligence
- ✅ **Data Preparation**: CSV sales data analysis and PDF document processing
- ✅ **Knowledge Base Creation**: Structured data organization with FAISS vector store
- ✅ **LLM Application**: Advanced data summaries with GPT-3.5-turbo
- ✅ **Chain Prompts**: Sequential analysis and recommendation generation
- ✅ **RAG System**: PDF document retrieval with semantic search
- ✅ **Memory Integration**: Conversation history tracking

### Part 2: LLMOps & Visualization
- ✅ **Model Evaluation**: Custom evaluation framework for response quality
- ✅ **Data Visualizations**:
  - Sales trends over time
  - Product performance comparisons
  - Regional analysis
  - Customer demographics and segmentation
  - Monthly sales performance
  - Customer satisfaction metrics
- ✅ **Streamlit UI**: Interactive web interface for user interaction

## 📋 Requirements

- Python 3.11+
- OpenAI API Key
- Required packages (see `requirements.txt`)

## 🛠️ Installation

1. **Clone the repository**
```bash
cd /Users/marialima/github/generative-ai/business-assistant
```

2. **Create and activate virtual environment**
```bash
python3 -m venv venv
source venv/bin/activate  # On macOS/Linux
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Set up environment variables**

Create a `.env` file in the project root:
```
OPENAI_API_KEY=your_api_key_here
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key_here
LANGCHAIN_PROJECT=business-assistant
```

**LangSmith Setup:**
- Sign up at [smith.langchain.com](https://smith.langchain.com)
- Get your API key from Settings
- Free tier includes 5,000 traces/month

## 📁 Project Structure

```
business-assistant/
├── business-insight.py      # Main analysis script
├── streamlit_app.py         # Streamlit web interface
├── requirements.txt         # Python dependencies
├── .env                     # Environment variables (create this)
├── sales_data.csv          # Business data (required)
├── pdf/                    # PDF documents folder (required)
│   └── *.pdf              # Business documents
└── README.md              # This file
```

## 🎮 Usage

### Option 1: Run Core Analysis Script

```bash
python3 business-insight.py
```

This will:
- Load and analyze sales data
- Process PDF documents
- Generate insights for predefined questions
- Display analysis and recommendations

### Option 2: Run Streamlit Web Interface (Recommended)

```bash
streamlit run streamlit_app.py
```

Then open your browser to `http://localhost:8501`

## 🖥️ Streamlit Interface Features

### 🏠 Dashboard
- Key business metrics overview
- Sales trends visualization
- Regional distribution analysis
- Detailed data summary

### 💬 AI Assistant
- Interactive chat interface
- Ask questions about the business data
- Get AI-powered insights combining:
  - CSV data analysis
  - PDF document retrieval
  - Conversation memory
- Suggested questions for quick insights

### 📈 Visualizations
- **Sales Analysis**: Trends and regional distribution
- **Product Performance**: Comparison and satisfaction metrics
- **Customer Insights**: Demographics and segmentation
- **Time-Based Analysis**: Monthly performance tracking

### 📊 Data Explorer
- Filter data by product, region, and demographics
- View and download filtered datasets
- Summary statistics

### 🔍 Model Evaluation (LangSmith Integration)
- **Criteria-based evaluation**: Relevance, Helpfulness, Accuracy, Clarity
- **Automatic tracing**: All interactions logged to LangSmith
- **No expected answers required**: Evaluation works with questions only
- **View conversation memory**: Track chat history

## 🔧 Configuration

### Data Requirements

1. **sales_data.csv** should contain columns:
   - `date`: Transaction date
   - `sales`: Sales amount
   - `product`: Product name
   - `region`: Geographic region
   - `customer_age`: Customer age
   - `customer_gender`: Customer gender
   - `customer_satisfaction`: Satisfaction score

2. **pdf/** folder should contain business documents for RAG system

## 🧪 Testing

The system includes built-in evaluation capabilities:

```python
# Test questions
questions = [
    "What are our top-selling products?",
    "How can we improve customer satisfaction based on sales trends?",
    "What regions need more attention?"
]
```

## 🤖 Technologies Used

- **LangChain**: Framework for LLM applications
- **OpenAI GPT-3.5-turbo**: Language model for insights
- **FAISS**: Vector store for document retrieval
- **Streamlit**: Web interface
- **Plotly**: Interactive visualizations
- **Pandas**: Data analysis
- **Python-dotenv**: Environment management

## 📊 Key Components

### RAG System
- PDF document loading and chunking
- FAISS vector store for semantic search
- Custom retrieval function for context-aware responses

### LLM Integration
- Prompt engineering for accurate responses
- Sequential chains for analysis → recommendations
- Memory integration for context retention

### Visualization
- Interactive Plotly charts
- Multiple analysis perspectives
- Export capabilities

## 🐛 Troubleshooting

### Common Issues

1. **ModuleNotFoundError**: Ensure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **OpenAI API Error**: Check your `.env` file has valid API key
   ```bash
   echo $OPENAI_API_KEY  # Should display your key
   ```

3. **No PDF documents found**: Ensure PDF files are in `pdf/` folder

4. **Data file not found**: Ensure `sales_data.csv` exists in project root

## 📝 Notes

- The system uses modern LangChain LCEL (LangChain Expression Language) syntax
- All chains use `.invoke()` method instead of deprecated `.run()`
- Conversation memory persists during session
- Visualizations are interactive and can be exported

## 🎓 Project Context

This project was developed as part of an Advanced Generative AI Capstone, demonstrating:
- End-to-end AI application development
- LLMOps best practices
- RAG system implementation
- Production-ready UI development

## � Deployment to Railway

Railway provides an easy way to deploy your Streamlit app to the cloud.

### Prerequisites
- GitHub account
- Railway account (sign up at [railway.app](https://railway.app))
- Your code pushed to a GitHub repository

### Deployment Steps

1. **Push your code to GitHub**
   ```bash
   git add .
   git commit -m "Prepare for Railway deployment"
   git push origin main
   ```

2. **Create a Railway account**
   - Go to [railway.app](https://railway.app)
   - Sign up with your GitHub account

3. **Create a new project**
   - Click "New Project"
   - Select "Deploy from GitHub repo"
   - Choose your repository

4. **Configure environment variables**
   - In Railway dashboard, go to your project
   - Click on "Variables" tab
   - Add the following variables:
     ```
     OPENAI_API_KEY=your_openai_api_key_here
     LANGCHAIN_TRACING_V2=true
     LANGCHAIN_API_KEY=your_langsmith_api_key_here
     LANGCHAIN_PROJECT=catalyst-ai-production
     ```

5. **Configure deployment settings**
   Railway should auto-detect your Streamlit app. If not, add these settings:
   - **Start Command**: `streamlit run streamlit_app.py --server.port=$PORT --server.address=0.0.0.0`
   - **Build Command**: `pip install -r requirements.txt`

6. **Deploy**
   - Railway will automatically deploy your app
   - You'll get a public URL (e.g., `your-app.railway.app`)
   - The app will redeploy automatically on every git push

### Important Notes

- **Data Files**: Ensure `sales_data.csv` and `pdf/` folder are in your repository
- **Port Configuration**: Railway automatically assigns a port via `$PORT` environment variable
- **Custom Domain**: You can add a custom domain in Railway settings
- **Monitoring**: Use Railway's built-in logs and metrics for monitoring
- **Costs**: Railway offers a free tier with limited hours; check pricing for production use

### Troubleshooting Railway Deployment

1. **Build fails**: Check Railway logs for missing dependencies
2. **App crashes**: Verify all environment variables are set correctly
3. **Port issues**: Ensure start command includes `--server.port=$PORT`
4. **File not found**: Confirm data files are committed to git (not in `.gitignore`)

## �📧 Support

For issues or questions, refer to the LangChain and Streamlit documentation:
- [LangChain Docs](https://python.langchain.com/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [OpenAI API Docs](https://platform.openai.com/docs/)
- [Railway Docs](https://docs.railway.app/)

---

**Built with ❤️ using LangChain, OpenAI, and Streamlit**
