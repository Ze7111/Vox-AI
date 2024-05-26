# ------------------------------------------------- regular imports -------------------------------------------------- #

import threading
import json
from   typing   import Callable
from   pydantic import ValidationError

# -------------------------------------------------- local imports --------------------------------------------------- #

from .pydantic_structures import DataItem                                                                  # type:ignore

# -------------------------------------------------- set up logging -------------------------------------------------- #

import  logging

logger: logging.Logger = logging.getLogger("rich")

# check_sigint: Callable[[], bool]             = lambda: False

# -------------------------------------------------------------------------------------------------------------------- #

class UTILS: # ....................................................................................................... #
    @staticmethod
    def ASYNC(func: Callable): # ..................................................................................... #
        def wrapper(*args, **kwargs):
            threading.Thread(target=func, args=args, kwargs=kwargs).start()
        return wrapper #                                                                                        return #
    # end ............................................. UTILS ............................................... -> ASYNC #

    @staticmethod
    def to_snake_case(text: str) -> str: # ........................................................................... #
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
    # end ............................................. UTILS .......................................... -> snake_case #
# end .......................................................................................................... UTILS #

# ---------------------------------------------------- JSON ---------------------------------------------------------- #

class HandleJson: # .................................................................................................. #
    data_path: str = ""
    
    def __init__(self, data_path: str) -> None: # .................................................................... #
        HandleJson.data_path = data_path
    # end ........................................... HandleJson ......................................... -> __init__ #
    
    @staticmethod
    def load() -> list[DataItem] | str: # .............................................................. #
        logger.info(f"loading data from {HandleJson.data_path}")
    
        with open(HandleJson.data_path, "r") as f:
            data: dict = json.load(f)

        try:
            loaded_data = [DataItem(**item) for item in data]
            logger.info("data loaded successfully")
            return loaded_data #                                                                                return #

        except ValidationError as e:
            logger.error(f"validation error while loading data: {e}")
            return str(e) #                                                                                     return #
    # end ........................................... HandleJson ............................................. -> load #

    @staticmethod
    def save(data: list[DataItem]) -> None: # ........................................................................ #
        logger.info(f"saving data to {HandleJson.data_path}")

        with open(HandleJson.data_path, "w") as f:
            json.dump(data, f, indent=4)

        logger.info(f"data saved to {HandleJson.data_path}")
    # end ........................................... HandleJson ............................................. -> save #
# end ..................................................................................................... HandleJson #
