#!/usr/bin/env python3

import os
import sys
import subprocess
import platform
import logging

# -------------------------------------------------- local imports --------------------------------------------------- #

from Server import main as server_main, Config, app

# ----------------------------------------------------- runtime ------------------------------------------------------ #

def setup_basic_logging():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

def check_python_version():
    required_major = 3
    required_minor = 8
    current = sys.version_info
    
    if current.major < required_major or (current.major == required_major and current.minor < required_minor):
        logging.error(f"Python {required_major}.{required_minor}+ required. You are using Python {current.major}.{current.minor}.{current.micro}")
        return False
    return True

def check_dependencies():
    try:
        import toml
        import fastapi
        import uvicorn
        import rich
        import pydantic
        import transformers
        import torch
        logging.info("Basic dependencies verified")
        return True
    except ImportError as e:
        logging.error(f"Missing dependency: {e}")
        logging.error("Please run: pip install -r requirements.txt")
        return False

def check_models():
    models_dir = os.path.join(os.getcwd(), "Server", "models")
    required_models = [
        "ggml-model-Q4_K_M-llama-3-8B.gguf",  # Main model
        "mmproj-model-f16.gguf"               # Image projection model
    ]
    
    missing_models = []
    for model in required_models:
        if not os.path.exists(os.path.join(models_dir, model)):
            missing_models.append(model)
    
    if missing_models:
        logging.warning(f"Missing models: {', '.join(missing_models)}")
        logging.warning("Some features may be limited. Please download the missing models.")
        return False
    
    logging.info("All required models are available")
    return True

def check_config():
    config_path = os.path.join(os.getcwd(), "server.toml")
    if not os.path.exists(config_path):
        logging.error(f"Configuration file not found: {config_path}")
        return False
    
    try:
        import toml
        with open(config_path, 'r') as f:
            config = toml.load(f)
        
        # Check if password is default
        if config.get("server", {}).get("password") == "VoxAI-Production-2024":
            logging.warning("⚠️ DEFAULT PASSWORD DETECTED ⚠️")
            logging.warning("Please change the password in server.toml for security.")
        
        return True
    except Exception as e:
        logging.error(f"Error reading configuration: {e}")
        return False

def main():
    setup_basic_logging()
    
    print("\n" + "="*60)
    print("🔥 VOX AI SERVER STARTUP 🔥".center(60))
    print("="*60 + "\n")
    
    logging.info(f"Platform: {platform.platform()}")
    logging.info(f"Python version: {platform.python_version()}")
    
    if not check_python_version():
        return 1
    
    if not check_dependencies():
        return 1
    
    check_models()  # Only warn, don't exit
    
    if not check_config():
        return 1
    
    try:
        logging.info("Starting Vox AI Server...")
        server_main()
        return 0
    except KeyboardInterrupt:
        logging.info("Server shutdown requested by user")
        return 0
    except Exception as e:
        logging.error(f"Failed to start server: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
