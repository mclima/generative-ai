#!/usr/bin/env python3
"""
Pre-download the Sentence Transformer model to cache it in the deployment.
This eliminates the first-use latency when matching resumes.
"""
from sentence_transformers import SentenceTransformer
import os

def download_model():
    """Download and cache the Sentence Transformer model"""
    model_name = 'all-MiniLM-L6-v2'
    print(f"Downloading Sentence Transformer model: {model_name}")
    print("This will cache the model for faster resume matching...")
    
    model = SentenceTransformer(model_name)
    
    print(f"✓ Model downloaded successfully!")
    print(f"✓ Model cached at: {model._model_card_vars.get('model_name', 'default cache location')}")
    print(f"✓ Model size: ~90MB")
    print("Resume matching will now be instant on first use!")

if __name__ == "__main__":
    download_model()
