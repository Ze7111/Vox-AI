# ------------------------------------------------- regular imports -------------------------------------------------- #

import base64
import logging
import requests
import threading

from   typing   import Callable
from   pydantic import ValidationError

# -------------------------------------------------- local imports --------------------------------------------------- #

import Server.ai.core.data_structures as data_structures                                                           # type:ignore

# -------------------------------------------------- set up logging -------------------------------------------------- #

logger: logging.Logger = logging.getLogger("rich")

# -------------------------------------------------------------------------------------------------------------------- #

class UTILS:
    @staticmethod
    def ASYNC(func: Callable):
        def wrapper(*args, **kwargs):
            threading.Thread(target=func, args=args, kwargs=kwargs).start()
        return wrapper #                                                                                          return
    # end                                                                                                          ASYNC

    @staticmethod
    def to_snake_case(text: str) -> str:
        for (index,char) in enumerate(text:=text.replace(" ","_").replace("-","_")):
            if char.isupper():
                text = (
                    text[:index]
                    + ( "_"
                        if (    index > 0
                            and not text[index-1] == "_"
                            and not text[index-1].isupper()
                        ) else ""
                    )
                    + ( text[index].lower()
                        if (index > len(text)-1 and not text[index+1].isupper())
                        else text[index]
                    )
                    + text[index+1:]
                )

        return text.lstrip("_").lower() #                                                                       return #
    # end                                                                                                   snake_case #
    
    @staticmethod
    def convert_url_to_base64(url: str) -> str:
        response = requests.get(url)

        if response.status_code != 200:
            raise Exception(f"Failed to get image: {url}")

        return base64.b64encode(response.content).decode()
    # end                                                                                                url_to_base64 #

    @staticmethod
    def convert_local_to_base64(path: str) -> str:
        with open(path, "rb") as file:
            return base64.b64encode(file.read()).decode('utf-8')
    # end                                                                                              local_to_base64 #
# end                                                                                                            UTILS #
