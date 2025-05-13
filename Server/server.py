# ------------------------------------------------- regular imports -------------------------------------------------- #

import os
import sys
import json
import logging
import uvicorn
import requests
import time

from typing            import Iterator
from fastapi           import FastAPI, Depends, HTTPException, status
from fastapi.security  import HTTPBasic, HTTPBasicCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pathlib           import Path
from rich.logging      import RichHandler
from rich.traceback    import install

# -------------------------------------------------- local imports --------------------------------------------------- #

from Server.config.read_config import Config
from Server.ai                 import Model, ChatRequest, ChatResponse, ImageData
from Server.tests.tests_runner import run_server_tests

# ------------------------------------------------------ set up ------------------------------------------------------ #

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

logger: logging.Logger = logging.getLogger("rich")
app:    FastAPI        = FastAPI(
    title="Vox AI API",
    description="API for Vox AI, an intelligent assistant for educational purposes",
    version="1.0.0",
)

# Add CORS middleware to allow cross-origin requests
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Security
security = HTTPBasic()

# Load the model asynchronously
def get_model():
    model_path = Path(os.getcwd(), "Server", "models", "ggml-model-Q4_K_M-llama-3-8B.gguf")
    image_path = Path(os.getcwd(), "Server", "models", "mmproj-model-f16.gguf")
    
    if not model_path.exists():
        logger.error(f"Model not found at {model_path}. Please download the model and place it in the correct location.")
        raise FileNotFoundError(f"Model not found at {model_path}")

    if not image_path.exists() and Config.max_images > 0:
        logger.warning(f"Image processor not found at {image_path}. Multimodal capabilities will be disabled.")
    
    return Model(
        model_path,
        image_processor_path=image_path if image_path.exists() else None,
        multi_model=image_path.exists()
    )

def get_model_lazy():
    if not hasattr(get_model_lazy, "model"):
        logger.info("Initializing model for the first time")
        try:
            get_model_lazy.model = get_model()
        except Exception as e:
            logger.error(f"Failed to initialize model: {e}")
            get_model_lazy.model = None
    return get_model_lazy.model

def authenticate(credentials: HTTPBasicCredentials = Depends(security)):
    if credentials.username != "admin" or credentials.password != Config.server_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Basic"},
        )
    return credentials.username

def normalize_chat_request(request: ChatRequest, model: Model) -> Iterator[str]:
    try:
        for response in model.predict(request):
            yield response.model_dump_json() + "\n"
    except Exception as e:
        logger.error(f"Error in chat prediction: {e}")
        error_response = ChatResponse(
            id="error",
            model="error",
            created=int(time.time()),
            index=0,
            role="assistant",
            content=f"Error processing your request: {str(e)}",
            finish_reason="error"
        )
        yield error_response.model_dump_json() + "\n"

# --------------------------------------------------- server --------------------------------------------------------- #

@app.get("/")
def root():
    return {"status": "Vox AI server is running", "version": "1.0.0"}

@app.post("/chat")
def chat(request: ChatRequest, username: str = Depends(authenticate)) -> StreamingResponse:
    model = get_model_lazy()
    if model is None:
        raise HTTPException(status_code=503, detail="Model not available")
    
    generator: Iterator[str] = normalize_chat_request(request, model)
    return StreamingResponse(
        generator, 
        media_type="application/json",
        headers={"X-User": username}
    )

@app.post("/login")
def login(username: str = Depends(authenticate)):
    return {"status": "success", "message": "Authentication successful"}

@app.get("/health")
def health_check():
    model = get_model_lazy()
    return {
        "status": "healthy" if model and model.is_loaded else "initializing",
        "model_loaded": bool(model and model.is_loaded),
        "version": "1.0.0"
    }

def main() -> None:
    try:
        Config.load("server.toml")
        logger.info(f"Starting server on {Config.server_ip}:{Config.server_port}")
        # Initialize model in background
        get_model_lazy()
        uvicorn.run(
            app, 
            host=Config.server_ip, 
            port=Config.server_port,
            log_level="info"
        )
    except FileNotFoundError as e:
        logger.error(f"Configuration file not found: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        logger.info("Server shutdown requested")
    except Exception as e:
        logger.error(f"Server error: {e}")
        sys.exit(1)
    finally:
        logger.info("Server shutdown complete")

# end                                                                                                             main #

main()