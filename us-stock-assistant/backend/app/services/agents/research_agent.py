"""
Research Agent for automated news gathering and analysis.
"""
from typing import Dict, Any, List
import asyncio
from sqlalchemy.orm import Session
from datetime import datetime

from app.services.news_service import NewsService
from app.services.ai_analysis_service import AIAnalysisService
from app.services.alert_service import AlertService
from app.models import Portfolio


class ResearchAgent:
    """
    LangGraph agent for automated research.
    Gathers news and analysis for portfolio stocks and stores results.
    """
    
    def __init__(self, db: Session, mcp_tools=None):
        self.db = db
        # Initialize news service with MCP tools
        if mcp_tools is None:
            from app.mcp.tools.news import NewsMCPTools
            mcp_tools = NewsMCPTools()
        self.news_service = NewsService(mcp_tools)
        self.ai_service = AIAnalysisService(api_key="test_key")  # Pass a test key
        self.alert_service = AlertService(db)
    
    async def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the research agent.
        
        Args:
            state: Workflow state containing context and results
            
        Returns:
            Updated workflow state
        """
        results = state.get("results", {})
        errors = state.get("errors", [])
        context = state.get("context", {})
        
        try:
            # Get user_id from context
            user_id = context.get("user_id")
            if not user_id:
                errors.append("Research agent error: user_id not provided in context")
                state["results"] = results
                state["errors"] = errors
                return state
            
            # Get user's portfolio
            from uuid import UUID
            portfolio = self.db.query(Portfolio).filter(
                Portfolio.user_id == UUID(user_id)
            ).first()
            
            if not portfolio or not portfolio.positions:
                results["research"] = {
                    "tickers_researched": 0,
                    "message": "No portfolio positions to research"
                }
                state["results"] = results
                return state
            
            # Get unique tickers from portfolio
            tickers = list(set([pos.ticker for pos in portfolio.positions]))
            
            # Gather research for all tickers in parallel
            research_results = await self._research_tickers_parallel(tickers, user_id)
            
            results["research"] = {
                "tickers_researched": len(tickers),
                "tickers": tickers,
                "summaries": research_results
            }
            
        except Exception as e:
            errors.append(f"Research agent error: {str(e)}")
        
        state["results"] = results
        state["errors"] = errors
        state["current_node"] = "research_agent"
        
        return state
    
    async def _research_tickers_parallel(
        self,
        tickers: List[str],
        user_id: str
    ) -> List[Dict[str, Any]]:
        """
        Research multiple tickers in parallel.
        
        Args:
            tickers: List of ticker symbols
            user_id: User ID for storing results
            
        Returns:
            List of research summaries
        """
        tasks = []
        for ticker in tickers:
            tasks.append(self._research_ticker(ticker, user_id))
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out errors
        summaries = []
        for result in results:
            if isinstance(result, dict) and "error" not in result:
                summaries.append(result)
        
        return summaries
    
    async def _research_ticker(
        self,
        ticker: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Research a single ticker.
        
        Args:
            ticker: Stock ticker symbol
            user_id: User ID for storing results
            
        Returns:
            Research summary
        """
        try:
            # Get recent news
            news_articles = await self.news_service.getStockNews(ticker, limit=10)
            
            if not news_articles:
                return {
                    "ticker": ticker,
                    "summary": "No recent news available",
                    "news_count": 0,
                    "sentiment": "neutral"
                }
            
            # Get sentiment analysis
            sentiment_data = await self.news_service.getStockSentiment(ticker)
            
            # Generate AI summary
            summary_prompt = f"""
            Summarize the following news articles for {ticker}:
            
            {self._format_news_for_summary(news_articles)}
            
            Provide a brief summary highlighting:
            1. Key developments
            2. Market sentiment
            3. Potential impact on stock price
            """
            
            ai_summary = await self.ai_service.generate_summary(summary_prompt)
            
            # Store results as notification
            from uuid import UUID
            self.alert_service.send_notification(
                user_id=UUID(user_id),
                notification_type="research_update",
                title=f"Research Update: {ticker}",
                message=ai_summary[:200] + "..." if len(ai_summary) > 200 else ai_summary,
                data={
                    "ticker": ticker,
                    "full_summary": ai_summary,
                    "news_count": len(news_articles),
                    "sentiment": sentiment_data.overall_sentiment.label,
                    "sentiment_score": sentiment_data.overall_sentiment.score,
                    "researched_at": datetime.utcnow().isoformat()
                }
            )
            
            return {
                "ticker": ticker,
                "summary": ai_summary,
                "news_count": len(news_articles),
                "sentiment": sentiment_data.overall_sentiment.label,
                "sentiment_score": sentiment_data.overall_sentiment.score
            }
            
        except Exception as e:
            return {
                "ticker": ticker,
                "error": str(e)
            }
    
    def _format_news_for_summary(self, news_articles: List[Dict[str, Any]]) -> str:
        """
        Format news articles for AI summarization.
        
        Args:
            news_articles: List of news article dictionaries
            
        Returns:
            Formatted string
        """
        formatted = []
        for article in news_articles[:5]:  # Limit to 5 most recent
            formatted.append(
                f"- {article.get('headline', 'No headline')} "
                f"({article.get('source', 'Unknown source')}, "
                f"{article.get('published_at', 'Unknown date')})"
            )
        return "\n".join(formatted)
    
    async def research_single_ticker(
        self,
        ticker: str,
        user_id: str
    ) -> Dict[str, Any]:
        """
        Research a single ticker (public method).
        
        Args:
            ticker: Stock ticker symbol
            user_id: User ID for storing results
            
        Returns:
            Research summary
        """
        return await self._research_ticker(ticker, user_id)
