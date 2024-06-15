import json
import logging
import os
import sys
from pathlib import Path

import ai.model_loader as model_loader
import ai.prelude as prelude
import database.access
# ------------ local imports ------------
import database.start
import requests
import uvicorn
from ai.pydantic_structures import BaseChatConfig, ChatRequest, ImageData
from ai.tests import RunTests
from fastapi import FastAPI
from rich.logging import RichHandler
from rich.traceback import install

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

install(show_locals=True)

def convert_url_to_base64(url: str) -> str:
    import base64
    import requests

    response = requests.get(url)

    if response.status_code != 200:
        raise Exception(f"Failed to get image: {url}")

    return base64.b64encode(response.content).decode()

def convert_local_to_base64(path: str) -> str:
    import base64

    with open(path, "rb") as file:
        return base64.b64encode(file.read()).decode('utf-8')

def run_db_tests() -> None:
    database.start._test()

def run_ai_tests() -> None:
    tests = RunTests()
    tests.next() # 1

    result: None | BaseException | ImportError = tests.next() # 2

    if isinstance(result, ImportError):
        prelude.installer.install(result.msg)

def see_if_working() -> None:
    # cwd/Server/ggml-model-Q4_K_M-v1_0-4B.gguf | ggml-model-Q4_K_M-llama-3-8B.gguf

    model = model_loader.Model(
        Path(os.getcwd(), "Server", "models", "ggml-model-Q4_K_M-llama-3-8B.gguf"),
        BaseChatConfig(
                max_images  = 1,
                max_tokens  = 8000,
                keep_in_mem = True
        ),
        image_processor_path=Path(os.getcwd(), "Server", "models", "mmproj-model-f16.gguf"),
        multi_model=True
    )

    while True:
        chat_request = ChatRequest(
            text   = input("\u001b[93m>>> \u001b[0m"),
        )

        if chat_request.text.strip() == "exit":
            break

        for thing in model.predict(chat_request):
            print(thing.content, end='', flush=True)


    print("\n")

if __name__ == "__main__":
    #run_db_tests()
    run_ai_tests()
    see_if_working()
