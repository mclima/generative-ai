"""
Pre-download FinBERT model during build/deployment to avoid runtime delays.
This script should be run during the build phase.
"""
import os
import logging

# Set HuggingFace cache to /app/.cache so it persists in deployment
os.environ['HF_HOME'] = '/app/.cache/huggingface'
os.environ['TRANSFORMERS_CACHE'] = '/app/.cache/huggingface'

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def download_finbert():
    """Download FinBERT model and tokenizer to cache."""
    try:
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        
        logger.info("Downloading FinBERT model (ProsusAI/finbert)...")
        logger.info("This may take a few minutes (~500MB download)...")
        
        # Download tokenizer
        tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert")
        logger.info("✓ Tokenizer downloaded successfully")
        
        # Download model
        model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert")
        logger.info("✓ Model downloaded successfully")
        
        # Verify model works
        model.eval()
        logger.info("✓ Model verified and ready to use")
        
        logger.info("=" * 60)
        logger.info("FinBERT model cached successfully!")
        logger.info("The model will now load instantly at runtime.")
        logger.info("=" * 60)
        
        return True
    except Exception as e:
        logger.error(f"Failed to download FinBERT model: {e}")
        logger.error("The application will fall back to keyword-based sentiment analysis.")
        return False

if __name__ == "__main__":
    download_finbert()
