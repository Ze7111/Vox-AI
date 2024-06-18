# ------------------------------------------------- regular imports -------------------------------------------------- #

import logging
import os

from   pathlib        import Path
from   rich.logging   import RichHandler
from   rich.traceback import install

# -------------------------------------------------- local imports --------------------------------------------------- #

import Server.database.access
import Server.database.start

from Server.ai import Model, ChatRequest, prelude
from Server.tests.tests import RunTests

# ------------------------------------------------------ set up ------------------------------------------------------ #

logger: logging.Logger = logging.getLogger("rich")

# ------------------------------------------------------- tests ------------------------------------------------------ #

def run_db_tests() -> None:
    #database.start._test()
    pass

def run_ai_tests() -> None:
    tests = RunTests()
    tests.next() # 1

    result: None | BaseException | ImportError = tests.next() # 2

    if isinstance(result, ImportError):
        prelude.install(result.msg)
        
def see_if_working() -> None:
    # cwd/Server/ggml-model-Q4_K_M-v1_0-4B.gguf | ggml-model-Q4_K_M-llama-3-8B.gguf

    model = Model(
        Path(os.getcwd(), "Server", "models", "ggml-model-Q4_K_M-llama-3-8B.gguf"),
        image_processor_path=Path(os.getcwd(), "Server", "models", "mmproj-model-f16.gguf"),
        multi_model=True
    )

    while True:
        chat_request = ChatRequest(
            text   = input("\u001b[92m>>> \u001b[0m"),
        )

        if chat_request.text.strip() == "exit":
            break
        
        if chat_request.text.strip() == "context":
            print(model.context)
            continue

        for thing in model.predict(chat_request):
            print(thing.content, end='', flush=True)

    print("\n")
        
def run_server_tests() -> None:
    #run_db_tests()
    run_ai_tests()
    #see_if_working()
    