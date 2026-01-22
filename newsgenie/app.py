import streamlit as st
import os
from dotenv import load_dotenv
from src.workflow import NewsGenieWorkflow
from datetime import datetime

load_dotenv()

st.set_page_config(
    page_title="NewsGenie - AI News Assistant",
    page_icon="🧞",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_css():
    with open("static/styles.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_css()

def initialize_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "workflow" not in st.session_state:
        st.session_state.workflow = None
    if "api_keys_configured" not in st.session_state:
        st.session_state.api_keys_configured = False

def check_api_keys():
    openai_key = os.getenv("OPENAI_API_KEY")
    gnews_key = os.getenv("GNEWS_API_KEY")
    tavily_key = os.getenv("TAVILY_API_KEY")
    
    if openai_key and gnews_key and tavily_key:
        if not st.session_state.workflow:
            try:
                st.session_state.workflow = NewsGenieWorkflow(
                    openai_api_key=openai_key,
                    gnews_api_key=gnews_key,
                    tavily_api_key=tavily_key
                )
                st.session_state.api_keys_configured = True
                return True
            except Exception as e:
                st.error(f"Error initializing workflow: {str(e)}")
                return False
        return True
    return False

def display_news_articles(articles):
    if not articles:
        st.info("No news articles found.")
        return
    
    for i, article in enumerate(articles, 1):
        with st.container():
            st.markdown(f"""
            <div class="news-card">
                <div class="news-title">{i}. {article['title']}</div>
                <div class="news-meta">📰 {article['source']} • 📅 {article['publishedAt'][:10]}</div>
                <p>{article['description']}</p>
                <a href="{article['url']}" target="_blank">Read more →</a>
            </div>
            """, unsafe_allow_html=True)

def main():
    initialize_session_state()
    
    st.markdown('<div class="main-header">🧞 NewsGenie</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Your AI-Powered News & Information Assistant</div>', unsafe_allow_html=True)
    
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        if not check_api_keys():
            st.warning("⚠️ API Keys Not Configured")
            st.markdown("""
            Please set up your API keys in a `.env` file:
            
            ```
            OPENAI_API_KEY=your_key_here
            GNEWS_API_KEY=your_key_here
            TAVILY_API_KEY=your_key_here
            ```
            
            **Get your API keys:**
            - [OpenAI API](https://platform.openai.com/api-keys)
            - [GNews API](https://gnews.io/)
            - [Tavily API](https://tavily.com/)
            """)
        else:
            st.success("✅ All API keys configured")
        
        st.divider()
        
        st.header("📰 Quick News Access")
        
        news_category = st.selectbox(
            "Select Category",
            ["Technology", "Finance", "Sports", "General", "Health", "Science", "Entertainment"],
            key="news_category"
        )
        
        if st.button("🔄 Get Latest News", use_container_width=True):
            if st.session_state.api_keys_configured:
                with st.spinner(f"Fetching {news_category.lower()} news..."):
                    query = f"What are the latest {news_category.lower()} news?"
                    result = st.session_state.workflow.process_query(query)
                    
                    st.session_state.messages.append({
                        "role": "user",
                        "content": query
                    })
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result["response"],
                        "news_results": result.get("news_results")
                    })
                    st.rerun()
        
        st.divider()
        
        if st.button("🗑️ Clear Chat History", use_container_width=True):
            st.session_state.messages = []
            st.rerun()
        
        st.divider()
        
        st.markdown("### 💡 Try asking:")
        st.markdown("""
        - "What's the latest in AI?"
        - "Tell me about climate change"
        - "Sports news today"
        - "What's happening with the stock market?"
        - "Explain artificial intelligence"
        """)
    
    if not st.session_state.api_keys_configured:
        st.info("👈 Please configure your API keys in the sidebar to get started.")
        return
    
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            
            if message["role"] == "assistant" and message.get("news_results"):
                news_data = message["news_results"]
                if news_data.get("success") and news_data.get("articles"):
                    with st.expander(f"📰 View {len(news_data['articles'])} News Articles"):
                        display_news_articles(news_data["articles"])
    
    if prompt := st.chat_input("Ask me anything or request news updates..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        with st.chat_message("user"):
            st.markdown(prompt)
        
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                result = st.session_state.workflow.process_query(prompt)
                
                if result["success"]:
                    st.markdown(result["response"])
                    
                    news_results = result.get("news_results")
                    if news_results and news_results.get("success") and news_results.get("articles"):
                        with st.expander(f"📰 View {len(news_results['articles'])} News Articles"):
                            display_news_articles(news_results["articles"])
                    
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": result["response"],
                        "news_results": news_results
                    })
                else:
                    error_msg = f"❌ Error: {result.get('error', 'Unknown error occurred')}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg
                    })

if __name__ == "__main__":
    main()
