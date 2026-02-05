"""Download ML models from external source if not available locally."""
import os
import pickle
import streamlit as st
from pathlib import Path

MODEL_FILES = {
    'tfidf.pkl': 'https://github.com/AtharvaMSable/Profyle-Sync/releases/download/v1.0/tfidf.pkl',
    'model.pkl': 'https://github.com/AtharvaMSable/Profyle-Sync/releases/download/v1.0/model.pkl'
}

def download_model(filename, url):
    """Download a model file from URL."""
    try:
        import requests
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True
    except Exception as e:
        st.error(f"Failed to download {filename}: {e}")
        return False

def ensure_models_exist():
    """Ensure model files exist, download if necessary."""
    for filename, url in MODEL_FILES.items():
        if not os.path.exists(filename):
            st.info(f"Downloading {filename}...")
            if download_model(filename, url):
                st.success(f"Downloaded {filename}")
            else:
                return False
    return True
