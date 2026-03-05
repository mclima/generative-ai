"""
Sentiment Analyzer using FinBERT for financial news.
"""
import os
import logging
import threading
from typing import List
from models.stock_models import NewsArticle

# Set HuggingFace cache to same location as build phase
os.environ['HF_HOME'] = '/app/.cache/huggingface'
os.environ['TRANSFORMERS_CACHE'] = '/app/.cache/huggingface'

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
            logger.info("Loading FinBERT model (ProsusAI/finbert)...")
            _tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
            _model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
            _model.eval()
            _model_loaded = True
            logger.info("FinBERT model loaded successfully")
        except Exception as e:
            _model_load_failed = True
            logger.error(f"Failed to load FinBERT model, falling back to keyword approach: {e}")


class SentimentAnalyzer:
    """Sentiment analyzer using FinBERT with keyword fallback."""
    
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
        """Initialize and load FinBERT model."""
        _load_finbert()
    
    def _finbert_score(self, text: str) -> str:
        """Run FinBERT inference. Returns sentiment label."""
        import torch
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
        # FinBERT: positive=0, negative=1, neutral=2
        label_map = {0: "positive", 1: "negative", 2: "neutral"}
        idx = int(probs.argmax())
        return label_map[idx]
    
    def _keyword_score(self, text: str) -> str:
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
        
        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        return "neutral"
    
    def analyze_sentiment(self, article: NewsArticle) -> str:
        """Analyze sentiment of a news article. Returns 'positive', 'negative', or 'neutral'."""
        text = f"{article.title} {article.description}"
        
        if _model_loaded and not _model_load_failed:
            try:
                return self._finbert_score(text)
            except Exception as e:
                logger.warning(f"FinBERT inference failed, using keyword fallback: {e}")
        
        return self._keyword_score(text)
    
    def analyze_batch(self, articles: List[NewsArticle]) -> List[NewsArticle]:
        """Analyze sentiment for multiple articles in parallel."""
        from concurrent.futures import ThreadPoolExecutor, as_completed
        
        if not articles:
            return articles
        
        # Process articles in parallel using thread pool
        with ThreadPoolExecutor(max_workers=min(len(articles), 4)) as executor:
            # Submit all articles for processing
            future_to_article = {
                executor.submit(self.analyze_sentiment, article): article 
                for article in articles
            }
            
            # Collect results as they complete
            for future in as_completed(future_to_article):
                article = future_to_article[future]
                try:
                    article.sentiment = future.result()
                except Exception as e:
                    logger.warning(f"Failed to analyze sentiment for article: {e}")
                    article.sentiment = "neutral"
        
        return articles
