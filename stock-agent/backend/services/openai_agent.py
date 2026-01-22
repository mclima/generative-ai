import os
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema import HumanMessage, SystemMessage
from models.stock_models import NewsArticle, AIInsight, InsightsResponse, StockData

class OpenAIAgent:
    def __init__(self):
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.llm = ChatOpenAI(
            model="gpt-4o-mini",
            temperature=0.3,
            openai_api_key=self.api_key
        )
    
    async def analyze_news_sentiment(self, news: List[NewsArticle]) -> List[NewsArticle]:
        try:
            for article in news:
                prompt = f"""Analyze the sentiment of this news article about a stock.
                
Title: {article.title}
Description: {article.description}

Respond with only one word: positive, negative, or neutral."""

                messages = [
                    SystemMessage(content="You are a financial sentiment analysis expert."),
                    HumanMessage(content=prompt)
                ]
                
                response = self.llm.invoke(messages)
                sentiment = response.content.strip().lower()
                
                if sentiment in ["positive", "negative", "neutral"]:
                    article.sentiment = sentiment
                else:
                    article.sentiment = "neutral"
            
            return news
        except Exception as e:
            print(f"Error analyzing sentiment: {str(e)}")
            return news
    
    async def generate_insights(
        self, 
        symbol: str, 
        stock_data: StockData, 
        news: List[NewsArticle],
        context: str = ""
    ) -> Dict[str, Any]:
        try:
            news_summary = "\n".join([f"- {article.title}" for article in news[:3]])
            
            prompt = f"""You are an expert stock analyst AI agent. Analyze the following stock and provide insights.

Stock: {symbol}
Current Price: ${stock_data.current_price}
Change: {stock_data.change_percent:.2f}%
Volume: {stock_data.volume:,}
P/E Ratio: {stock_data.pe_ratio}
52-Week Range: ${stock_data.low_52week} - ${stock_data.high_52week}

Recent News:
{news_summary}

{f"Historical Context: {context}" if context else ""}

Provide:
1. A brief summary (2-3 sentences) of the stock's current situation
2. Exactly 3 specific insights categorized as bullish, bearish, or neutral

Format your response as JSON with this structure:
{{
    "summary": "your summary here",
    "insights": [
        {{"type": "bullish/bearish/neutral", "title": "insight title", "description": "insight description"}},
        ...
    ]
}}"""

            messages = [
                SystemMessage(content="You are an expert financial analyst providing actionable stock insights."),
                HumanMessage(content=prompt)
            ]
            
            response = self.llm.invoke(messages)
            content = response.content.strip()
            
            if content.startswith("```json"):
                content = content[7:]
            if content.endswith("```"):
                content = content[:-3]
            content = content.strip()
            
            import json
            result = json.loads(content)
            
            return {
                "summary": result.get("summary", "Analysis in progress..."),
                "insights": result.get("insights", [])
            }
            
        except Exception as e:
            print(f"Error generating insights: {str(e)}")
            return {
                "summary": f"AI analysis for {symbol} is currently being processed. The stock is trading at ${stock_data.current_price} with a {stock_data.change_percent:.2f}% change.",
                "insights": [
                    {
                        "type": "neutral",
                        "title": "Price Movement",
                        "description": f"The stock has moved {stock_data.change_percent:.2f}% with volume of {stock_data.volume:,} shares."
                    },
                    {
                        "type": "neutral",
                        "title": "52-Week Performance",
                        "description": f"Trading within a 52-week range of ${stock_data.low_52week} to ${stock_data.high_52week}."
                    }
                ]
            }
