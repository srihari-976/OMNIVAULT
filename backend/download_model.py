"""
Llama 3.2 3B Model Downloader
Downloads and caches the model from HuggingFace
"""

import os
import sys
from huggingface_hub import snapshot_download, login
from config import Config
from tqdm import tqdm

def download_model():
    """Download Llama 3.2 3B model from HuggingFace"""
    print("="*70)
    print(" Llama 3.2 3B Model Downloader")
    print("="*70)
    print(f"\nModel: {Config.MODEL_NAME}")
    print(f"Cache Directory: {Config.MODEL_CACHE_DIR}")
    print(f"\nNote: This will download approximately 6-7 GB of data.")
    print("="*70)
    
    try:
        # Login to HuggingFace
        print("\n📝 Authenticating with HuggingFace...")
        if not Config.HUGGINGFACE_TOKEN:
            print("❌ Error: HUGGINGFACE_TOKEN not found!")
            print("Please set your token in the .env file")
            return False
        
        login(token=Config.HUGGINGFACE_TOKEN)
        print("✓ Authentication successful!")
        
        # Create cache directory
        os.makedirs(Config.MODEL_CACHE_DIR, exist_ok=True)
        
        # Download model
        print(f"\n📥 Downloading model: {Config.MODEL_NAME}")
        print("This may take several minutes depending on your internet connection...\n")
        
        snapshot_download(
            repo_id=Config.MODEL_NAME,
            cache_dir=Config.MODEL_CACHE_DIR,
            token=Config.HUGGINGFACE_TOKEN,
            resume_download=True
        )
        
        print("\n✅ Model downloaded successfully!")
        print(f"✓ Model cached in: {Config.MODEL_CACHE_DIR}")
        print("\nYou can now start the backend server with: python app.py")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error downloading model: {str(e)}")
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Verify your HuggingFace token is valid")
        print("3. Ensure you have access to the Llama model")
        print("4. Check available disk space (need ~10GB free)")
        return False


if __name__ == "__main__":
    print("\n")
    success = download_model()
    print("\n" + "="*70)
    
    if success:
        print("Ready to start!")
        sys.exit(0)
    else:
        print("Download failed. Please check the errors above.")
        sys.exit(1)
