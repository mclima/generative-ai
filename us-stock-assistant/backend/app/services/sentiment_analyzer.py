"""
Sentiment Analyzer for news articles using FinBERT.

This service provides sentiment analysis for financial news articles
using ProsusAI/finbert, a BERT model fine-tuned on financial text.
"""
import logging
import threading
from typing import List, Literal, Optional
from pydantic import BaseModel

from app.mcp.tools.news import NewsArticle

logger = logging.getLogger(__name__)

_model = None
_tokenizer = None
_model_lock = threading.Lock()
_model_loaded = False
_model_load_failed = False


def _load_finbert():
    """Load FinBERT model lazily on first use (thread-safe)."""
    global _model, _tokenizer, _model_loaded, _model_load_failed
    with _model_lock:
        if _model_loaded or _model_load_failed:
            return
        try:
            from transformers import AutoTokenizer, AutoModelForSequenceClassification
            import torch
            logger.info("Loading FinBERT model (ProsusAI/finbert)...")
            _tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
            _model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
            _model.eval()
            _model_loaded = True
            logger.info("FinBERT model loaded successfully")
        except Exception as e:
            _model_load_failed = True
            logger.error(f"Failed to load FinBERT model, falling back to keyword approach: {e}")


class SentimentScore(BaseModel):
    """Sentiment score for a news article."""
    label: Literal["positive", "negative", "neutral"]
    score: float  # -1 to 1 scale
    confidence: float  # 0 to 1 scale


class StockSentiment(BaseModel):
    """Aggregated sentiment for a stock."""
    ticker: str
    overall_sentiment: SentimentScore
    article_count: int
    recent_articles: List[NewsArticle]


class SentimentAnalyzer:
    """
    Sentiment analyzer using FinBERT (ProsusAI/finbert).

    Falls back to keyword-based approach if the model cannot be loaded.
    """

    POSITIVE_KEYWORDS = [
        "gain", "gains", "up", "rise", "rises", "rising", "surge", "surges",
        "rally", "rallies", "bullish", "growth", "profit", "profits",
        "beat", "beats", "exceed", "exceeds", "strong", "positive",
        "upgrade", "upgrades", "outperform", "buy", "success", "successful",
        "high", "higher", "record", "best", "improve", "improves", "improvement"
    ]

    NEGATIVE_KEYWORDS = [
        "loss", "losses", "down", "fall", "falls", "falling", "drop", "drops",
        "decline", "declines", "bearish", "weak", "weakness", "miss", "misses",
        "downgrade", "downgrades", "underperform", "sell", "concern", "concerns",
        "low", "lower", "worst", "poor", "risk", "risks", "cut", "cuts",
        "layoff", "layoffs", "lawsuit", "investigation"
    ]

    def __init__(self):
        """Initialize Sentiment Analyzer and begin loading FinBERT in background."""
        _load_finbert()

    def _finbert_score(self, text: str) -> tuple[str, float, float]:
        """Run FinBERT inference on text. Returns (label, score, confidence)."""
        import torch
        # Truncate to 512 tokens max
        inputs = _tokenizer(
            text,
            return_tensors="pt",
            truncation=True,
            max_length=512,
            padding=True
        )
        with torch.no_grad():
            outputs = _model(**inputs)
        probs = torch.softmax(outputs.logits, dim=-1)[0]
        # FinBERT label order: positive=0, negative=1, neutral=2
        label_map = {0: "positive", 1: "negative", 2: "neutral"}
        idx = int(probs.argmax())
        label = label_map[idx]
        confidence = float(probs[idx])
        pos_prob = float(probs[0])
        neg_prob = float(probs[1])
        score = pos_prob - neg_prob  # -1 to 1
        return label, score, confidence

    def _keyword_score(self, text: str) -> tuple[str, float, float]:
        """Fallback keyword-based scoring."""
        import re
        text_lower = text.lower()
        positive_count = sum(
            1 for kw in self.POSITIVE_KEYWORDS
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower)
        )
        negative_count = sum(
            1 for kw in self.NEGATIVE_KEYWORDS
            if re.search(r'\b' + re.escape(kw) + r'\b', text_lower)
        )
        total = positive_count + negative_count
        if total == 0:
            return "neutral", 0.0, 0.5
        if positive_count > negative_count:
            score = min(1.0, (positive_count - negative_count) / total)
            return "positive", score, min(1.0, total / 5.0)
        elif negative_count > positive_count:
            score = max(-1.0, -(negative_count - positive_count) / total)
            return "negative", score, min(1.0, total / 5.0)
        return "neutral", 0.0, 0.6

    def _calculate_sentiment_score(self, text: str) -> tuple[str, float, float]:
        if _model_loaded and not _model_load_failed:
            try:
                return self._finbert_score(text)
            except Exception as e:
                logger.warning(f"FinBERT inference failed, using keyword fallback: {e}")
        return self._keyword_score(text)

    def analyzeSentiment(self, article: NewsArticle) -> SentimentScore:
        text = f"{article.headline} {article.summary}"
        label, score, confidence = self._calculate_sentiment_score(text)
        logger.debug(f"Sentiment '{article.headline[:60]}': {label} score={score:.2f} conf={confidence:.2f}")
        return SentimentScore(label=label, score=score, confidence=confidence)

    def getStockSentiment(
        self,
        ticker: str,
        articles: List[NewsArticle]
    ) -> StockSentiment:
        if not articles:
            return StockSentiment(
                ticker=ticker,
                overall_sentiment=SentimentScore(label="neutral", score=0.0, confidence=0.0),
                article_count=0,
                recent_articles=[]
            )

        sentiments = [self.analyzeSentiment(a) for a in articles]

        total_weighted_score = sum(s.score * s.confidence for s in sentiments)
        total_confidence = sum(s.confidence for s in sentiments)
        avg_score = total_weighted_score / total_confidence if total_confidence > 0 else 0.0

        if avg_score > 0.1:
            overall_label = "positive"
        elif avg_score < -0.1:
            overall_label = "negative"
        else:
            overall_label = "neutral"

        avg_confidence = total_confidence / len(sentiments)

        logger.info(f"Aggregated sentiment for {ticker}: {overall_label} (score={avg_score:.2f}, conf={avg_confidence:.2f}) from {len(articles)} articles")

        return StockSentiment(
            ticker=ticker,
            overall_sentiment=SentimentScore(
                label=overall_label,
                score=avg_score,
                confidence=avg_confidence
            ),
            article_count=len(articles),
            recent_articles=articles
        )
