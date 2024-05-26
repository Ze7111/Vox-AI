# ------------------------------------------------- regular imports -------------------------------------------------- #

import os
import gc
from types import FrameType
import torch
import signal
import threading

from tqdm               import tqdm
from PIL                import Image
from typing             import Callable, Optional, Union
from transformers       import AutoProcessor, AutoModelForCausalLM                                         # type:ignore

# -------------------------------------------------- set up logging -------------------------------------------------- #

import  logging
logger: logging.Logger = logging.getLogger("rich")

# ----------------------------------------------------- AI ----------------------------------------------------------- #

class SigintHandler: # ............................................................................................... #
    _instance: Optional["SigintHandler"] = None

    def __new__(cls, ignore_msg: str = "") -> 'SigintHandler': # ..................................................... #
        if cls._instance is None:
            cls._instance               = super(SigintHandler, cls).__new__(cls)
            cls._instance.__initialized = False                                                            # type:ignore

        return cls._instance #                                                                                  return #
    # end ........................................ SigintHandler .......................................... -> __new__ #

    def __init__(self, ignore_msg: str = "") -> None: # ...................................................................... #
        if self.__initialized:                                                                             # type:ignore
            return #                                                                                              return

        if threading.current_thread() is not threading.main_thread():
            raise RuntimeError("'SigintHandler' MUST be in the main thread")

        self.__base_sigint = signal.getsignal(signal.SIGINT)
        self.__recv        = False
        self.__ignore_msg  = ignore_msg
        self.__initialized = True
    # end ........................................ SigintHandler ......................................... -> __init__ #

    def sigint_handle(self, *_: Union[int, Callable[[int, FrameType | None], None]]) -> None: # ...................... #
        logger.warning(f"SIGINT received, ignored. {self.__ignore_msg}")
        self.__recv = True
    # end ........................................ SigintHandler .................................... -> sigint_handle #

    def __enter__(self) -> Callable[[], bool]: # ..................................................................... #
        signal.signal(signal.SIGINT, self.sigint_handle)                                                   # type:ignore
        return self.sigint_received #                                                                           return #
    # end ........................................ SigintHandler ........................................ -> __enter__ #

    def __exit__(self, *_: tuple) -> None: # ......................................................................... #
        signal.signal(signal.SIGINT, self.__base_sigint)
    # end ........................................ SigintHandler ......................................... -> __exit__ #

    def sigint_received(self): # ..................................................................................... #
        return self.__recv     #                                                                                return #
    # end ........................................ SigintHandler .................................. -> sigint_received #
# end .................................................................................................. SigintHandler #

# -------------------------------------------------------------------------------------------------------------------- #

class GITImageProcessor: # ........................................................................................... #
    processor:    Optional[AutoProcessor]        = None
    model:        Optional[AutoModelForCausalLM] = None
    device:       Optional[str]                  = None

    def __init__(self) -> None: # .................................................................................... #
        with SigintHandler("attempting to shut down model and pre-processor loading") as siR:
            self.__check_sigint:        Callable[[], bool] = siR                             # sigint received checker
            self.__processor_cache_dir: str                = "models/git-large-coco"
            self.__model_cache_dir:     str                = "models/git-large-coco-model"
            self.__processor_file_path: str                = os.path.join(self.__processor_cache_dir, "processor.pt")
            self.__model_file_path:     str                = os.path.join(self.__model_cache_dir    , "model.pt")

            threading.Thread(target=self.__load_all).start()
    # end ........................................ GITImageProcessor ..................................... -> __init__ #

    # ---------------------------------------------------------------------------------------------------------------- #

    def __check(self, message: str) -> None: # ....................................................................... #
        if self.__check_sigint() : # if SIGINT received
            self.shutdown(message)
            raise KeyboardInterrupt(message)
    # end ........................................ GITImageProcessor ...................................... -> __check #

    # ---------------------------------------------------------------------------------------------------------------- #

    def __load_processor(self) -> None: # ............................................................................ #
        if os.path.exists(self.__processor_file_path):
            logger.debug("attempting to load pre-processor from local cache")
            GITImageProcessor.processor = torch.load(self.__processor_file_path)
            logger.info("pre-processor loaded from local cache")
        else:
            os.makedirs(self.__processor_cache_dir, exist_ok=True)

            logger. warning("pre-processor not found in local cache, downloading from Hugging Face")
            GITImageProcessor.processor = AutoProcessor.from_pretrained("microsoft/git-large-coco")

            logger.debug("saving pre-processor to local cache")
            torch. save(GITImageProcessor.processor, self.__processor_file_path)
            logger.info("saved pre-processor.")

        try:
            self.__check("SIGINT received, shutting down pre-processor...")
        except KeyboardInterrupt:
            return #                                                                                            return #
    # end ........................................ GITImageProcessor ............................. -> __load_processor #

    def __load_model(self) -> None: # ................................................................................ #
        if os.path.exists(self.__model_file_path):
            logger.debug("attempting to load model from local cache")
            GITImageProcessor.model = torch.load(self.__model_file_path)
            logger.info("model loaded from local cache")
        else:
            os.makedirs(self.__model_cache_dir, exist_ok=True)

            logger. warning("model not found in local cache, downloading from Hugging Face")
            GITImageProcessor.model = AutoModelForCausalLM.from_pretrained("microsoft/git-large-coco")

            logger.debug("saving model to local cache")
            torch.save(GITImageProcessor.model, self.__model_file_path)
            logger.info("saved model.")

        try:
            self.__check("SIGINT received, shutting down model...")
        except KeyboardInterrupt:
            return #                                                                                            return #
    # end ........................................ GITImageProcessor ................................. -> __load_model #

    # ---------------------------------------------------------------------------------------------------------------- #

    def __load_all(self) -> None: # ............................................................................ ASYNC #
        # ------------------------------------------------------------------------------------------------------------ #

        logger.info("loading model and pre-processor")

        # ------------------------------------------------------------------------------------------------------------ #

        try:
            self.__load_processor()
        except Exception as e:
            logger.error(f"failed to load model: {e}")

        # ------------------------------------------------------------------------------------------------------------ #

        try:
            self.__load_model()
        except Exception as e:
            logger.error(f"failed to load model: {e}")
            self.shutdown("failed to load model, shutting down...")
            return #                                                                                            return #

        # ------------------------------------------------------------------------------------------------------------ #

        GITImageProcessor.device = "cuda" if torch.cuda.is_available() else "cpu" # set device to cuda if available

        if GITImageProcessor.model is not None:
            GITImageProcessor.model.to(GITImageProcessor.device)

        try:
            self.__check(f"SIGINT received, stopping model from moving to '{GITImageProcessor.device}'...")
        except KeyboardInterrupt:
            return #                                                                                            return #

        # ------------------------------------------------------------------------------------------------------------ #

        logger.info("model and pre-processor loaded")
    # end ........................................ GITImageProcessor ................................... -> __load_all #

    # ---------------------------------------------------------------------------------------------------------------- #

    def __generate_caption(self, img: str) -> str: # ................................................................. #
        logger.warning("waiting for model and pre-processor to load") if (
               GITImageProcessor.processor is None
            or GITImageProcessor.model     is None
            or GITImageProcessor.device    is None
        ) else (
            logger.info("model and pre-processor loaded")
        )

        while (
                GITImageProcessor.processor is None
            or GITImageProcessor.model     is None
            or GITImageProcessor.device    is None
        ):
            if self.__check_sigint():
                logger.error("SIGINT received, shutting down caption generation")
                return "" #                                                                                     return #

        try:
            self.__check("SIGINT received, shutting down caption generation")
        except KeyboardInterrupt:
            return "" #                                                                                         return #

        image = Image.open(os.path.abspath(img))
        logger.debug(f"image opened: {img}")

        inp = GITImageProcessor.processor(images=image,return_tensors="pt").to(GITImageProcessor.device)
        logger.debug("image pre-processed")

        generated_ids = GITImageProcessor.model.generate(pixel_values=inp.pixel_values,max_length=50)
        logger.debug("caption generated")

        generated_caption = GITImageProcessor.processor.batch_decode(generated_ids,skip_special_tokens=True)[0]
        logger.debug(f"decoded caption: {generated_caption}")

        return generated_caption #                                                                              return #
    # end ........................................ GITImageProcessor ........................... -> __generate_caption #

    # ---------------------------------------------------------------------------------------------------------------- #

    def generate_caption(self, img: str) -> str: # ................................................................... #
        if threading.current_thread() is not threading.main_thread():
            raise RuntimeError("'generate_caption' MUST be in the main thread")

        with SigintHandler("running caption generation, SIGINT ignored") as siR:
            self.__check_sigint = siR
            return self.__generate_caption(img)
    # end ........................................ GITImageProcessor ............................. -> generate_caption #
    
    @classmethod
    def shutdown(cls, reason: str) -> None: # ....................................................................... #
        logger.error(reason)

        # -------------------------------------------- free up resources --------------------------------------------- #

        if 'processor' in dir(cls): del GITImageProcessor.processor
        if 'model'     in dir(cls): del GITImageProcessor.model
        if 'device'    in dir(cls): del GITImageProcessor.device

        # ------------------------------------------------------------------------------------------------------------ #

        gc.collect() # force garbage collection to free up memory

        # -- set globals to None to avoid accidental use of freed resources -- #

        GITImageProcessor.processor = None
        GITImageProcessor.model     = None
        GITImageProcessor.device    = None

        # ------------------------------------------------------------------------------------------------------------ #

        logger.info("Resources freed, final shutdown complete.")
    # end ........................................ GITImageProcessor ..................................... -> shutdown #
# end .............................................................................................. GITImageProcessor #
