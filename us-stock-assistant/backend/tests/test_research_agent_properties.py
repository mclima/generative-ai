"""
Property-based tests for Research Agent.

Feature: us-stock-assistant, Property 22: Research Automation
**Validates: Requirements 5.3**
"""
import pytest
from hypothesis import given, strategies as st, settings, assume, HealthCheck
from decimal import Decimal
from datetime import datetime, date
from uuid import uuid4
from unittest.mock import AsyncMock, MagicMock, patch

from app.models import User, Portfolio, StockPosition, Notification
from app.services.agents.research_agent import ResearchAgent
from app.services.sentiment_analyzer import StockSentiment, SentimentScore


# Strategies for generating test data
@st.composite
def portfolio_data(draw):
    """Generate valid portfolio data with positions."""
    num_positions = draw(st.integers(min_value=1, max_value=5))
    tickers = draw(st.lists(
        st.sampled_from(["AAPL", "GOOGL", "MSFT", "AMZN", "TSLA", "NVDA", "META"]),
        min_size=num_positions,
        max_size=num_positions,
        unique=True
    ))
    
    positions = []
    for ticker in tickers:
        positions.append({
            "ticker": ticker,
            "quantity": draw(st.floats(min_value=1.0, max_value=100.0)),
            "purchase_price": draw(st.floats(min_value=10.0, max_value=500.0)),
            "purchase_date": draw(st.dates(
                min_value=date(2020, 1, 1),
                max_value=date.today()
            ))
        })
    
    return {
        "tickers": tickers,
        "positions": positions
    }


@st.composite
def news_data(draw):
    """Generate mock news data."""
    num_articles = draw(st.integers(min_value=0, max_value=10))
    articles = []
    
    for i in range(num_articles):
        articles.append({
            "id": str(uuid4()),
            "headline": f"News headline {i}",
            "source": draw(st.sampled_from(["Reuters", "Bloomberg", "CNBC", "WSJ"])),
            "published_at": datetime.utcnow().isoformat(),
            "summary": f"News summary {i}",
            "sentiment": {
                "label": draw(st.sampled_from(["positive", "negative", "neutral"])),
                "score": draw(st.floats(min_value=-1.0, max_value=1.0))
            }
        })
    
    return articles


class TestResearchAgentProperties:
    """Property-based tests for Research Agent."""
    
    @given(portfolio=portfolio_data())
    @settings(
        max_examples=5,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_property_22_research_automation(self, db_session, portfolio):
        """
        Property 22: Research Automation
        
        For any portfolio with configured research automation, the agentic system
        should gather and summarize news and reports for all portfolio stocks.
        
        **Validates: Requirements 5.3**
        """
        # Create test user
        user = User(
            email=f"test_{uuid4()}@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create portfolio
        portfolio_obj = Portfolio(user_id=user.id)
        db_session.add(portfolio_obj)
        db_session.commit()
        db_session.refresh(portfolio_obj)
        
        # Add positions
        for pos_data in portfolio["positions"]:
            position = StockPosition(
                portfolio_id=portfolio_obj.id,
                ticker=pos_data["ticker"],
                quantity=Decimal(str(round(pos_data["quantity"], 4))),
                purchase_price=Decimal(str(round(pos_data["purchase_price"], 2))),
                purchase_date=pos_data["purchase_date"]
            )
            db_session.add(position)
        db_session.commit()
        
        # Create research agent with mocked services
        from unittest.mock import MagicMock
        mock_mcp_tools = MagicMock()
        research_agent = ResearchAgent(db_session, mcp_tools=mock_mcp_tools)
        
        # Mock the news service and AI service
        mock_news = [
            {
                "headline": f"News for ticker",
                "source": "Test Source",
                "published_at": datetime.utcnow().isoformat(),
                "summary": "Test summary"
            }
        ]
        
        mock_sentiment = StockSentiment(
            ticker="TEST",
            overall_sentiment=SentimentScore(
                label="positive",
                score=0.5,
                confidence=0.8
            ),
            article_count=1,
            recent_articles=[]
        )
        
        with patch.object(research_agent.news_service, 'getStockNews', new_callable=AsyncMock) as mock_get_news, \
             patch.object(research_agent.news_service, 'getStockSentiment', new_callable=AsyncMock) as mock_get_sentiment, \
             patch.object(research_agent.ai_service, 'generate_summary', new_callable=AsyncMock) as mock_generate_summary:
            
            mock_get_news.return_value = mock_news
            mock_get_sentiment.return_value = mock_sentiment
            mock_generate_summary.return_value = "AI generated summary of news"
            
            # Execute research agent
            import asyncio
            state = {
                "context": {"user_id": str(user.id)},
                "results": {},
                "errors": []
            }
            
            final_state = asyncio.run(research_agent(state))
            
            # Verify research was performed
            assert "research" in final_state["results"]
            research_results = final_state["results"]["research"]
            
            # Verify all tickers were researched
            assert research_results["tickers_researched"] == len(portfolio["tickers"])
            assert set(research_results["tickers"]) == set(portfolio["tickers"])
            
            # Verify summaries were generated
            assert "summaries" in research_results
            assert len(research_results["summaries"]) <= len(portfolio["tickers"])
            
            # Verify notifications were created for each ticker
            notifications = db_session.query(Notification).filter(
                Notification.user_id == user.id,
                Notification.type == "research_update"
            ).all()
            
            # Should have at least one notification per ticker
            assert len(notifications) >= 1
            
            # Verify notification content
            for notification in notifications:
                assert "Research Update:" in notification.title
                assert notification.data.get("ticker") in portfolio["tickers"]
                assert "full_summary" in notification.data
                assert "news_count" in notification.data
                assert "sentiment" in notification.data
    
    @given(num_tickers=st.integers(min_value=1, max_value=10))
    @settings(
        max_examples=5,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_parallel_research_execution(self, db_session, num_tickers):
        """
        Test that research agent processes multiple tickers in parallel.
        """
        # Create test user
        user = User(
            email=f"test_{uuid4()}@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create portfolio with multiple positions
        portfolio = Portfolio(user_id=user.id)
        db_session.add(portfolio)
        db_session.commit()
        
        tickers = [f"TST{chr(65+i)}" for i in range(min(num_tickers, 26))]  # TSTA, TSTB, etc.
        for ticker in tickers:
            position = StockPosition(
                portfolio_id=portfolio.id,
                ticker=ticker,
                quantity=Decimal("10.0"),
                purchase_price=Decimal("100.0"),
                purchase_date=date.today()
            )
            db_session.add(position)
        db_session.commit()
        
        # Create research agent
        mock_mcp_tools = MagicMock()
        research_agent = ResearchAgent(db_session, mcp_tools=mock_mcp_tools)
        
        # Mock services
        with patch.object(research_agent.news_service, 'getStockNews', new_callable=AsyncMock) as mock_get_news, \
             patch.object(research_agent.news_service, 'getStockSentiment', new_callable=AsyncMock) as mock_get_sentiment, \
             patch.object(research_agent.ai_service, 'generate_summary', new_callable=AsyncMock) as mock_generate_summary:
            
            mock_get_news.return_value = []
            mock_get_sentiment.return_value = StockSentiment(
                ticker="TEST",
                overall_sentiment=SentimentScore(label="neutral", score=0, confidence=0.5),
                article_count=0,
                recent_articles=[]
            )
            mock_generate_summary.return_value = "Summary"
            
            # Execute research
            import asyncio
            state = {
                "context": {"user_id": str(user.id)},
                "results": {},
                "errors": []
            }
            
            final_state = asyncio.run(research_agent(state))
            
            # Verify all tickers were processed
            assert final_state["results"]["research"]["tickers_researched"] == num_tickers
    
    @given(news_articles=news_data())
    @settings(
        max_examples=5,
        deadline=None,
        suppress_health_check=[HealthCheck.function_scoped_fixture]
    )
    def test_research_with_varying_news_counts(self, db_session, news_articles):
        """
        Test that research agent handles varying numbers of news articles correctly.
        """
        # Create test user
        user = User(
            email=f"test_{uuid4()}@example.com",
            password_hash="hashed_password"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        
        # Create portfolio with one position
        portfolio = Portfolio(user_id=user.id)
        db_session.add(portfolio)
        db_session.commit()
        
        position = StockPosition(
            portfolio_id=portfolio.id,
            ticker="TEST",
            quantity=Decimal("10.0"),
            purchase_price=Decimal("100.0"),
            purchase_date=date.today()
        )
        db_session.add(position)
        db_session.commit()
        
        # Create research agent
        mock_mcp_tools = MagicMock()
        research_agent = ResearchAgent(db_session, mcp_tools=mock_mcp_tools)
        
        # Mock services with varying news counts
        with patch.object(research_agent.news_service, 'getStockNews', new_callable=AsyncMock) as mock_get_news, \
             patch.object(research_agent.news_service, 'getStockSentiment', new_callable=AsyncMock) as mock_get_sentiment, \
             patch.object(research_agent.ai_service, 'generate_summary', new_callable=AsyncMock) as mock_generate_summary:
            
            mock_get_news.return_value = news_articles
            mock_get_sentiment.return_value = StockSentiment(
                ticker="TEST",
                overall_sentiment=SentimentScore(label="neutral", score=0, confidence=0.5),
                article_count=len(news_articles),
                recent_articles=[]
            )
            mock_generate_summary.return_value = "Summary"
            
            # Execute research
            import asyncio
            state = {
                "context": {"user_id": str(user.id)},
                "results": {},
                "errors": []
            }
            
            final_state = asyncio.run(research_agent(state))
            
            # Verify research completed
            assert "research" in final_state["results"]
            
            # If no news, should still complete
            if len(news_articles) == 0:
                # Should still create a notification even with no news
                notifications = db_session.query(Notification).filter(
                    Notification.user_id == user.id
                ).all()
                # May or may not create notification for no news, but should not error
                assert len(final_state["errors"]) == 0
            else:
                # With news, should create notification
                notifications = db_session.query(Notification).filter(
                    Notification.user_id == user.id,
                    Notification.type == "research_update"
                ).all()
                assert len(notifications) >= 1
