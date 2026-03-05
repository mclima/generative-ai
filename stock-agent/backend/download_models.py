"""
Pre-download FinBERT model during build/deployment to avoid runtime delays.
This script should be run during the build phase.
"""
import os
import logging

# Set HuggingFace cache to ~/.cache/huggingface (default HF location that persists on Railway)
cache_dir = os.path.expanduser("~/.cache/huggingface")
os.environ['HF_HOME'] = cache_dir
os.environ['TRANSFORMERS_CACHE'] = cache_dir

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def download_finbert():
    """Download FinBERT model and tokenizer to cache."""
    try:
        logger.info("=" * 60)
        logger.info(f"Cache directory: {cache_dir}")
        logger.info("=" * 60)
        
        from transformers import AutoTokenizer, AutoModelForSequenceClassification
        
        logger.info("Downloading FinBERT model (ProsusAI/finbert)...")
        logger.info("This may take a few minutes (~500MB download)...")
        logger.info("Please wait...")
        
        # Download tokenizer
        logger.info("Downloading tokenizer...")
        tokenizer = AutoTokenizer.from_pretrained("ProsusAI/finbert", cache_dir=cache_dir)
        logger.info("✓ Tokenizer downloaded successfully")
        
        # Download model
        logger.info("Downloading model weights (~500MB)...")
        model = AutoModelForSequenceClassification.from_pretrained("ProsusAI/finbert", cache_dir=cache_dir)
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
