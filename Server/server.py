# ------------------------------------------------- regular imports -------------------------------------------------- #

import os
import sys
import json
import logging
import uvicorn
import requests

from typing            import Iterator
from fastapi           import FastAPI
from fastapi.responses import StreamingResponse
from pathlib           import Path
from rich.logging      import RichHandler
from rich.traceback    import install

# -------------------------------------------------- local imports --------------------------------------------------- #

from Server.config.read_config import Config
from Server.ai                 import Model, ChatRequest, ChatResponse
from Server.tests.tests_runner import run_server_tests

# ------------------------------------------------------ set up ------------------------------------------------------ #

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

logger: logging.Logger = logging.getLogger("rich")
app:    FastAPI        = FastAPI()
model:  Model          = Model(
    Path(os.getcwd(),  "Server", "models", "ggml-model-Q4_K_M-llama-3-8B.gguf"),
    image_processor_path=Path(os.getcwd(), "Server", "models", "mmproj-model-f16.gguf"),
    multi_model=True
) # this is an asynchronous call to load the model.

install(show_locals=True)

# --------------------------------------------------- server --------------------------------------------------------- #

def normalize_chat_request(request: ChatRequest) -> Iterator[str]:
    for response in model.predict(request): # response = Iterator[ChatResponse]
        yield response.model_dump_json() + "\n"

@app.post("/chat")
def chat(request: ChatRequest) -> StreamingResponse:
    generator: Iterator[str] = normalize_chat_request(request)
    return StreamingResponse(generator, media_type="application/json")

@app.get("/items/{item_id}")
def read_item(item_id):
    return {"item_id": item_id}

def main() -> None:
    Config.load("server.toml")
    uvicorn.run(app, host=Config.server_ip, port=Config.server_port)
    run_server_tests()
# end                                                                                                             main #

main()