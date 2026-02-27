"""
AI Analysis Service for generating stock and portfolio analysis using LLMs.

This service uses LangChain with OpenAI or Anthropic to provide AI-powered insights.
"""
import logging
from typing import List, Dict, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field
import asyncio

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser

from app.config import get_settings

logger = logging.getLogger(__name__)


# Data models for analysis context and results
class HistoricalDataPoint(BaseModel):
    """Historical price data point."""
    date: datetime
    open: float
    high: float
    low: float
    close: float
    volume: int


class NewsArticle(BaseModel):
    """News article with sentiment."""
    headline: str
    source: str
    published_at: datetime
    summary: Optional[str] = None
    sentiment_label: Optional[str] = None
    sentiment_score: Optional[float] = None


class FinancialMetrics(BaseModel):
    """Financial metrics for a stock."""
    ticker: str
    pe_ratio: Optional[float] = None
    eps: Optional[float] = None
    dividend_yield: Optional[float] = None
    beta: Optional[float] = None
    fifty_two_week_high: Optional[float] = None
    fifty_two_week_low: Optional[float] = None


class MarketConditions(BaseModel):
    """Overall market conditions."""
    market_sentiment: Optional[str] = None
    sp500_change: Optional[float] = None
    nasdaq_change: Optional[float] = None
    dow_change: Optional[float] = None


class AnalysisContext(BaseModel):
    """Context data for stock analysis."""
    historical_data: List[HistoricalDataPoint] = Field(default_factory=list)
    news: List[NewsArticle] = Field(default_factory=list)
    financial_metrics: Optional[FinancialMetrics] = None
    market_conditions: Optional[MarketConditions] = None


class PriceAnalysis(BaseModel):
    """Price trend analysis."""
    trend: Optional[Literal["bullish", "bearish", "neutral"]] = "neutral"
    support: Optional[float] = None
    resistance: Optional[float] = None
    volatility: Optional[Literal["high", "medium", "low"]] = "medium"


class SentimentAnalysis(BaseModel):
    """Sentiment analysis results."""
    overall: Optional[Literal["positive", "negative", "neutral"]] = "neutral"
    score: Optional[float] = Field(default=0.0)
    news_count: int = 0


class StockAnalysis(BaseModel):
    """Complete stock analysis result."""
    ticker: str
    summary: str
    price_analysis: PriceAnalysis
    sentiment_analysis: SentimentAnalysis
    recommendations: List[str]
    risks: List[str]
    generated_at: datetime


class RebalancingSuggestion(BaseModel):
    """Portfolio rebalancing suggestion."""
    action: Literal["buy", "sell", "hold"]
    ticker: str
    reason: str
    suggested_amount: Optional[float] = None


class PortfolioAnalysis(BaseModel):
    """Complete portfolio analysis result."""
    overall_health: Literal["good", "fair", "poor"]
    diversification_score: float = Field(ge=0.0, le=100.0)
    risk_level: Literal["high", "medium", "low"]
    rebalancing_suggestions: List[RebalancingSuggestion]
    underperforming_stocks: List[str]
    opportunities: List[str]


class AIAnalysisService:
    """
    Service for generating AI-powered stock and portfolio analysis.
    
    Implements:
    - Stock analysis with price trends, volatility, sentiment, recommendations, and risks
    - Portfolio analysis with health score, diversification, and rebalancing suggestions
    - Timeout handling (10-second limit)
    - Structured output using Pydantic models
    """
    
    # Analysis timeout in seconds
    ANALYSIS_TIMEOUT = 10
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize AI Analysis Service.
        
        Args:
            api_key: OpenAI API key (optional, defaults to config)
        """
        settings = get_settings()
        self.api_key = api_key or settings.openai_api_key
        
        if not self.api_key:
            logger.warning("No OpenAI API key provided - AI analysis will not be available")
            self.llm = None
        else:
            # Initialize LangChain with OpenAI
            self.llm = ChatOpenAI(
                model="gpt-4",
                temperature=0.3,
                api_key=self.api_key,
                request_timeout=self.ANALYSIS_TIMEOUT
            )
        
        # Set up output parsers
        self.stock_analysis_parser = PydanticOutputParser(pydantic_object=StockAnalysis)
        self.portfolio_analysis_parser = PydanticOutputParser(pydantic_object=PortfolioAnalysis)
        
        # Create prompt templates
        self._setup_prompts()
    
    def _setup_prompts(self):
        """Set up prompt templates for analysis."""
        
        # Stock analysis prompt
        self.stock_analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a professional financial analyst providing stock analysis.
Analyze the provided stock data and generate a comprehensive analysis.

{format_instructions}

Be concise but thorough. Focus on actionable insights."""),
            ("user", """Analyze the following stock:

Ticker: {ticker}

Historical Price Data (last 30 days):
{historical_data}

Recent News:
{news}

Financial Metrics:
{financial_metrics}

Market Conditions:
{market_conditions}

Provide a complete analysis including:
1. Price trend analysis (bullish/bearish/neutral) with support/resistance levels
2. Volatility assessment (high/medium/low)
3. Sentiment analysis based on news
4. Specific recommendations for investors
5. Key risks to be aware of

Generate the analysis in the specified JSON format.""")
        ])
        
        # Portfolio analysis prompt
        self.portfolio_analysis_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a professional portfolio manager providing portfolio analysis.
Analyze the provided portfolio data and generate comprehensive recommendations.

{format_instructions}

Be concise but thorough. Focus on actionable insights."""),
            ("user", """Analyze the following portfolio:

Portfolio Positions:
{portfolio_positions}

Portfolio Metrics:
{portfolio_metrics}

Market Conditions:
{market_conditions}

Provide a complete analysis including:
1. Overall portfolio health assessment (good/fair/poor)
2. Diversification score (0-100)
3. Risk level assessment (high/medium/low)
4. Specific rebalancing suggestions with actions (buy/sell/hold)
5. List of underperforming stocks
6. Investment opportunities

Generate the analysis in the specified JSON format.""")
        ])
    
    def _format_historical_data(self, data: List[HistoricalDataPoint]) -> str:
        """Format historical data for prompt."""
        if not data:
            return "No historical data available"
        
        lines = []
        for point in data[-30:]:  # Last 30 days
            lines.append(
                f"{point.date.strftime('%Y-%m-%d')}: "
                f"Open ${point.open:.2f}, Close ${point.close:.2f}, "
                f"High ${point.high:.2f}, Low ${point.low:.2f}, "
                f"Volume {point.volume:,}"
            )
        return "\n".join(lines)
    
    def _format_news(self, news: List[NewsArticle]) -> str:
        """Format news articles for prompt."""
        if not news:
            return "No recent news available"
        
        lines = []
        for article in news[:10]:  # Top 10 articles
            sentiment = ""
            if article.sentiment_label:
                sentiment = f" [{article.sentiment_label}]"
            
            lines.append(
                f"- {article.headline}{sentiment}\n"
                f"  Source: {article.source}, "
                f"Date: {article.published_at.strftime('%Y-%m-%d')}"
            )
            
            if article.summary:
                lines.append(f"  Summary: {article.summary}")
        
        return "\n".join(lines)
    
    def _format_financial_metrics(self, metrics: Optional[FinancialMetrics]) -> str:
        """Format financial metrics for prompt."""
        if not metrics:
            return "No financial metrics available"
        
        lines = [
            f"P/E Ratio: {metrics.pe_ratio if metrics.pe_ratio else 'N/A'}",
            f"EPS: ${metrics.eps if metrics.eps else 'N/A'}",
            f"Dividend Yield: {metrics.dividend_yield}%" if metrics.dividend_yield else "Dividend Yield: N/A",
            f"Beta: {metrics.beta if metrics.beta else 'N/A'}",
            f"52-Week High: ${metrics.fifty_two_week_high if metrics.fifty_two_week_high else 'N/A'}",
            f"52-Week Low: ${metrics.fifty_two_week_low if metrics.fifty_two_week_low else 'N/A'}"
        ]
        return "\n".join(lines)
    
    def _format_market_conditions(self, conditions: Optional[MarketConditions]) -> str:
        """Format market conditions for prompt."""
        if not conditions:
            return "No market conditions data available"
        
        lines = []
        if conditions.market_sentiment:
            lines.append(f"Market Sentiment: {conditions.market_sentiment}")
        if conditions.sp500_change is not None:
            lines.append(f"S&P 500 Change: {conditions.sp500_change:+.2f}%")
        if conditions.nasdaq_change is not None:
            lines.append(f"NASDAQ Change: {conditions.nasdaq_change:+.2f}%")
        if conditions.dow_change is not None:
            lines.append(f"DOW Change: {conditions.dow_change:+.2f}%")
        
        return "\n".join(lines) if lines else "No market conditions data available"
    
    async def analyzeStock(self, ticker: str, context: AnalysisContext) -> StockAnalysis:
        """
        Generate AI analysis for a stock.
        
        Args:
            ticker: Stock ticker symbol
            context: Analysis context with historical data, news, metrics, and market conditions
        
        Returns:
            StockAnalysis with comprehensive analysis
        
        Raises:
            ValueError: If analysis cannot be completed reliably
            TimeoutError: If analysis exceeds timeout limit
        """
        if not self.llm:
            raise ValueError(
                "AI analysis is not available. OpenAI API key is not configured. "
                "Please set the OPENAI_API_KEY environment variable."
            )
        
        ticker = ticker.upper()
        logger.info(f"Starting AI analysis for {ticker}")
        
        try:
            # Format context data for prompt
            historical_data_str = self._format_historical_data(context.historical_data)
            news_str = self._format_news(context.news)
            financial_metrics_str = self._format_financial_metrics(context.financial_metrics)
            market_conditions_str = self._format_market_conditions(context.market_conditions)
            
            # Create the prompt
            prompt = self.stock_analysis_prompt.format_messages(
                ticker=ticker,
                historical_data=historical_data_str,
                news=news_str,
                financial_metrics=financial_metrics_str,
                market_conditions=market_conditions_str,
                format_instructions=self.stock_analysis_parser.get_format_instructions()
            )
            
            # Execute analysis with timeout
            try:
                response = await asyncio.wait_for(
                    self.llm.ainvoke(prompt),
                    timeout=self.ANALYSIS_TIMEOUT
                )
            except asyncio.TimeoutError:
                logger.error(f"Analysis timeout for {ticker}")
                raise TimeoutError(
                    f"Analysis for {ticker} exceeded the {self.ANALYSIS_TIMEOUT}-second time limit. "
                    "Please try again later."
                )
            
            # Parse the response
            try:
                analysis = self.stock_analysis_parser.parse(response.content)
                analysis.ticker = ticker
                analysis.generated_at = datetime.now()
                
                logger.info(f"Successfully completed AI analysis for {ticker}")
                return analysis
            
            except Exception as e:
                logger.error(f"Failed to parse analysis response for {ticker}: {e}")
                raise ValueError(
                    f"Unable to generate reliable analysis for {ticker}. "
                    "The AI response could not be parsed correctly. Please try again."
                )
        
        except TimeoutError:
            raise
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during analysis for {ticker}: {e}")
            raise ValueError(
                f"Unable to generate analysis for {ticker} due to an unexpected error: {str(e)}. "
                "Please try again later."
            )
    
    async def analyzePortfolio(
        self,
        portfolio_positions: List[Dict],
        portfolio_metrics: Dict,
        market_conditions: Optional[MarketConditions] = None
    ) -> PortfolioAnalysis:
        """
        Generate AI analysis for a portfolio.
        
        Args:
            portfolio_positions: List of portfolio positions with ticker, quantity, value, gain/loss
            portfolio_metrics: Portfolio metrics including total value, diversity score, etc.
            market_conditions: Optional market conditions data
        
        Returns:
            PortfolioAnalysis with health score, diversification, and rebalancing suggestions
        
        Raises:
            ValueError: If analysis cannot be completed reliably
            TimeoutError: If analysis exceeds timeout limit
        """
        if not self.llm:
            raise ValueError(
                "AI analysis is not available. OpenAI API key is not configured. "
                "Please set the OPENAI_API_KEY environment variable."
            )
        
        logger.info("Starting AI portfolio analysis")
        
        try:
            # Format portfolio data for prompt
            positions_str = self._format_portfolio_positions(portfolio_positions)
            metrics_str = self._format_portfolio_metrics(portfolio_metrics)
            market_conditions_str = self._format_market_conditions(market_conditions)
            
            # Create the prompt
            prompt = self.portfolio_analysis_prompt.format_messages(
                portfolio_positions=positions_str,
                portfolio_metrics=metrics_str,
                market_conditions=market_conditions_str,
                format_instructions=self.portfolio_analysis_parser.get_format_instructions()
            )
            
            # Execute analysis with timeout
            try:
                response = await asyncio.wait_for(
                    self.llm.ainvoke(prompt),
                    timeout=self.ANALYSIS_TIMEOUT
                )
            except asyncio.TimeoutError:
                logger.error("Portfolio analysis timeout")
                raise TimeoutError(
                    f"Portfolio analysis exceeded the {self.ANALYSIS_TIMEOUT}-second time limit. "
                    "Please try again later."
                )
            
            # Parse the response
            try:
                analysis = self.portfolio_analysis_parser.parse(response.content)
                
                logger.info("Successfully completed AI portfolio analysis")
                return analysis
            
            except Exception as e:
                logger.error(f"Failed to parse portfolio analysis response: {e}")
                raise ValueError(
                    "Unable to generate reliable portfolio analysis. "
                    "The AI response could not be parsed correctly. Please try again."
                )
        
        except TimeoutError:
            raise
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Unexpected error during portfolio analysis: {e}")
            raise ValueError(
                f"Unable to generate portfolio analysis due to an unexpected error: {str(e)}. "
                "Please try again later."
            )
    
    def _format_portfolio_positions(self, positions: List[Dict]) -> str:
        """Format portfolio positions for prompt."""
        if not positions:
            return "No positions in portfolio"
        
        lines = []
        for pos in positions:
            ticker = pos.get("ticker", "UNKNOWN")
            quantity = pos.get("quantity", 0)
            current_value = pos.get("current_value", 0)
            gain_loss = pos.get("gain_loss", 0)
            gain_loss_percent = pos.get("gain_loss_percent", 0)
            
            lines.append(
                f"- {ticker}: {quantity} shares, "
                f"Value: ${current_value:,.2f}, "
                f"Gain/Loss: ${gain_loss:+,.2f} ({gain_loss_percent:+.2f}%)"
            )
        
        return "\n".join(lines)
    
    def _format_portfolio_metrics(self, metrics: Dict) -> str:
        """Format portfolio metrics for prompt."""
        if not metrics:
            return "No portfolio metrics available"
        
        lines = [
            f"Total Value: ${metrics.get('total_value', 0):,.2f}",
            f"Total Gain/Loss: ${metrics.get('total_gain_loss', 0):+,.2f} ({metrics.get('total_gain_loss_percent', 0):+.2f}%)",
            f"Daily Gain/Loss: ${metrics.get('daily_gain_loss', 0):+,.2f}",
            f"Diversity Score: {metrics.get('diversity_score', 0):.1f}/100"
        ]
        
        # Add performance by period if available
        performance = metrics.get("performance_by_period", {})
        if performance:
            lines.append("\nPerformance by Period:")
            for period, value in performance.items():
                lines.append(f"  {period}: {value:+.2f}%")
        
        return "\n".join(lines)

    async def generate_summary(self, prompt: str) -> str:
        """
        Generate a summary using the LLM.
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            Generated summary text
        """
        if not self.llm:
            logger.warning("LLM not available - returning placeholder summary")
            return "AI analysis not available - no API key configured"
        
        try:
            response = await self.llm.ainvoke(prompt)
            return response.content
        except Exception as e:
            logger.error(f"Error generating summary: {e}")
            return f"Error generating summary: {str(e)}"
