import requests
from fastapi import FastAPI
import uvicorn
import logging
from rich.logging import RichHandler
from rich.traceback import install

# ------------ local imports ------------
import database.start
import database.access

FORMAT = "%(message)s"
logging.basicConfig(
    level="NOTSET", format=FORMAT, datefmt="[%X]", handlers=[RichHandler()]
)

install(show_locals=True)

def run_tests() -> None:
    database.start._test()

if __name__ == "__main__":
    run_tests()
    