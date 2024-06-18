# ------------------------------------------------- regular imports -------------------------------------------------- #

import signal
import logging
import threading

from types  import FrameType
from typing import Callable, Optional, Union

# -------------------------------------------------- set up logging -------------------------------------------------- #

logger: logging.Logger = logging.getLogger("rich")

# ----------------------------------------------------- AI ----------------------------------------------------------- #

class SigintHandler:
    _instance: Optional["SigintHandler"] = None

    def __new__(cls, ignore_msg: str = "") -> 'SigintHandler':
        if cls._instance is None:
            cls._instance               = super(SigintHandler, cls).__new__(cls)
            cls._instance.__initialized = False                                                            # type:ignore

        return cls._instance #                                                                                    return
    # end                                                                                                      __new__ #

    def __init__(self, ignore_msg: str = "") -> None:
        if self.__initialized:                                                                             # type:ignore
            return #                                                                                              return

        if threading.current_thread() is not threading.main_thread():
            raise RuntimeError("'SigintHandler' MUST be in the main thread")

        self.__base_sigint = signal.getsignal(signal.SIGINT)
        self.__recv        = False
        self.__ignore_msg  = ignore_msg
        self.__initialized = True
    # end                                                                                                     __init__ #

    def sigint_handle(self, *_: Union[int, Callable[[int, FrameType | None], None]]) -> None:
        logger.warning(f"SIGINT received, ignored. {self.__ignore_msg}")
        self.__recv = True
    # end                                                                                                sigint_handle #

    def __enter__(self) -> Callable[[], bool]:
        signal.signal(signal.SIGINT, self.sigint_handle)                                                   # type:ignore
        return self.sigint_received #                                                                             return
    # end                                                                                                    __enter__ #

    def __exit__(self, *_: tuple) -> None:
        signal.signal(signal.SIGINT, self.__base_sigint)
    # end                                                                                                     __exit__ #

    def sigint_received(self):
        return self.__recv #                                                                                      return
    # end                                                                                              sigint_received #
# end                                                                                                    SigintHandler #
