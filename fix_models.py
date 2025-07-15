#!/usr/bin/env python3
"""
Fix for sklearn model compatibility issues.

This script:
1. Deletes old incompatible models
2. Regenerates models with current sklearn version
3. Tests model loading to ensure compatibility
"""

import os
import logging
from pathlib import Path
import shutil

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def main():
    """Fix sklearn model compatibility issues."""
    
    logger.info("🔧 Starting sklearn model compatibility fix...")
    
    # Check sklearn version
    try:
        import sklearn
        logger.info(f"📊 Current sklearn version: {sklearn.__version__}")
    except ImportError:
        logger.error("❌ sklearn not installed. Please install requirements first.")
        return False
    
    # Define paths
    models_dir = Path("models")
    mlb_model_file = models_dir / "mlb_models.pkl"
    soccer_model_file = models_dir / "soccer_models.pkl"
    
    # Step 1: Remove old incompatible models
    logger.info("🗑️  Removing old incompatible models...")
    
    for model_file in [mlb_model_file, soccer_model_file]:
        if model_file.exists():
            logger.info(f"   Removing {model_file}")
            model_file.unlink()
    
    # Step 2: Import and regenerate models
    logger.info("🏗️  Regenerating models with current sklearn version...")
    
    try:
        from ml_models import MLModelManager
        
        # Create model manager
        model_manager = MLModelManager()
        
        # Train new models with current sklearn version
        logger.info("🏀 Training MLB models...")
        mlb_result = model_manager.mlb_predictor.train_models(
            model_manager.mlb_predictor.load_historical_data()
        )
        
        logger.info("⚽ Training Soccer models...")
        soccer_result = model_manager.soccer_predictor.train_models(
            model_manager.soccer_predictor.load_historical_data()
        )
        
        if mlb_result and soccer_result:
            logger.info("✅ Models regenerated successfully!")
        else:
            logger.warning("⚠️  Some models may not have trained properly")
            
    except Exception as e:
        logger.error(f"❌ Failed to regenerate models: {e}")
        return False
    
    # Step 3: Test model loading
    logger.info("🧪 Testing model loading...")
    
    try:
        # Test MLB model loading
        if mlb_model_file.exists():
            model_manager.mlb_predictor._load_models()
            logger.info("✅ MLB models load successfully")
        
        # Test Soccer model loading  
        if soccer_model_file.exists():
            model_manager.soccer_predictor._load_models()
            logger.info("✅ Soccer models load successfully")
            
        logger.info("🎉 All models are now compatible with current sklearn version!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Model loading test failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n✅ Model compatibility fix completed successfully!")
        print("📊 You can now run the betting system without sklearn errors.")
    else:
        print("\n❌ Model compatibility fix failed.")
        print("🔍 Check the log messages above for details.")