#!/usr/bin/env python3
"""
Pre-download the Sentence Transformer model to cache it in the deployment.
This eliminates the first-use latency when matching resumes.
"""
import os
from sentence_transformers import SentenceTransformer

# Set cache directory for HuggingFace models
os.environ["HF_HOME"] = "/app/.hf_cache"
os.environ["TRANSFORMERS_CACHE"] = "/app/.hf_cache"

def download_model():
    """
    Pre-download the Sentence Transformer model to cache it.
    This script is run during the Railway build phase via nixpacks.toml
    """
    model_name = 'all-MiniLM-L6-v2'
    cache_folder = "/app/.hf_cache"
    
    print(f"Downloading Sentence Transformer model: {model_name}")
    print(f"Cache folder: {cache_folder}")
    print("This will cache the model for faster resume matching...")
    
    model = SentenceTransformer(model_name, cache_folder=cache_folder)
    
    print(f"✓ Model downloaded successfully!")
    print(f"✓ Model cached at: {model._model_card_vars.get('model_name', 'default cache location')}")
    print(f"✓ Model size: ~90MB")
    print("Resume matching will now be instant on first use!")

if __name__ == "__main__":
    download_model()
