import os
from dotenv import load_dotenv
from src.news_api import GNewsAPI
from src.web_search import WebSearchTool
from langchain_openai import ChatOpenAI

load_dotenv()

print("🧞 NewsGenie API Test Script")
print("=" * 50)
print()

print("Testing API Keys...")
print("-" * 50)

openai_key = os.getenv("OPENAI_API_KEY")
gnews_key = os.getenv("GNEWS_API_KEY")
tavily_key = os.getenv("TAVILY_API_KEY")

if openai_key:
    try:
        llm = ChatOpenAI(model="gpt-4o-mini", api_key=openai_key, temperature=0)
        response = llm.invoke("Say 'test successful'")
        print("✅ OpenAI API key is valid")
        print(f"   Response: {response.content[:50]}...")
    except Exception as e:
        print(f"❌ OpenAI API key is invalid: {str(e)}")
else:
    print("❌ OpenAI API key not found in .env")

print()

if gnews_key:
    news_api = GNewsAPI(api_key=gnews_key)
    result = news_api.fetch_top_headlines("general", max_results=1)
    if result["success"]:
        print("✅ GNews API key is valid")
        if result["articles"]:
            print(f"   Sample article: {result['articles'][0]['title'][:50]}...")
    else:
        print(f"❌ GNews API key is invalid: {result['error']}")
else:
    print("❌ GNews API key not found in .env")

print()

if tavily_key:
    search_tool = WebSearchTool(api_key=tavily_key)
    result = search_tool.search("test query", max_results=1)
    if result["success"]:
        print("✅ Tavily API key is valid")
        if result["results"]:
            print(f"   Sample result: {result['results'][0]['title'][:50]}...")
    else:
        print(f"❌ Tavily API key is invalid: {result['error']}")
else:
    print("❌ Tavily API key not found in .env")

print()
print("=" * 50)
print("Test complete!")
print()

if openai_key and gnews_key and tavily_key:
    print("🎉 All API keys are configured!")
    print("   You can now run: streamlit run app.py")
else:
    print("⚠️  Some API keys are missing. Please check your .env file.")
