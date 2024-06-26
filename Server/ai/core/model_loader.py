# ------------------------------------------------- regular imports -------------------------------------------------- #

import gc
import os
import threading

from pathlib            import Path
from concurrent.futures import TimeoutError
from typing             import Iterator, Optional, Union

from llama_cpp import ChatCompletionRequestMessage

from Server.config.read_config import Config

try:
    from llama_cpp                   import CreateChatCompletionStreamResponse, Llama
    from llama_cpp.llama_chat_format import Llava15ChatHandler, MoondreamChatHandler
    from llama_cpp.llama_speculative import LlamaPromptLookupDecoding
except ImportError:
    pass

# -------------------------------------------------- local imports --------------------------------------------------- #

import logging

from Server.ai.context.chat_context    import ChatContext
from Server.ai.core.data_structures    import BaseChatConfig, ChatRequest, ChatResponse
from Server.ai.core.errors             import ModelFailedToLoad, ModelNotFoundError, ModelTookTooLongToLoad

# -------------------------------------------------- set up logging -------------------------------------------------- #

logger: logging.Logger = logging.getLogger("rich")

# -------------------------------------------------- LoadModel ------------------------------------------------------- #

class Hub:
    def __init__(self, repo_id: str, file_name: str = "q4_1.gguf", clip_name: str = "*mmproj*") -> None:
        self.model_name: str = repo_id
        self.file_name: str = file_name
        self.clip_name: str = clip_name
    # end                                                                                                     __init__ #
# end                                                                                                              Hub #

class Model:
    """ this class will contain the high-level managed api for the following:
            - loading the model
            - chat
            - unloading the model

        the model will be loaded in the __init__ function and unloaded
        in the__del__ function

        ------------------------------------------------------------------------
        ```python
        >>> from pathlib import Path

        >>> model = Model(
        ...     Path("..", "Bunny-Llama-3-8B-V-gguf"),
        ...     BaseChatConfig(...)
        ... )

        >>> # alternatively you can use a hub model (will install if not found)

        >>> # model = Model(
        ... #     Hub("BAAI/Bunny-Llama-3-8B-V-gguf"),
        ... #     BaseChatConfig(...)
        ... # )

        >>> response: ChatResponse = model.predict(
        ...     request=ChatRequest(...)
        ... )

        >>> # process a batch of requests asynchronously (if possible)
        >>> batch_response: list[ChatResponse] = model.predict_batch(
        ...     requests=[ChatRequest(...), ...]
        ... )

        >>> for chunk in response:
        ...    print(chunk.text)

        >>> for response_instance in batch_response:
        ...     with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        ...         # each element in the bath response is a inst of a ChatResponse
        ...         # so we need to iterate over the batch response async
        ...         # and then iterate over each chunk in the response in sync with
        ...         # the batch response chunk iteration so if we are predicting 10
        ...         # requests in a batch, we will get 10 response instances to
        ...         # iterate over

        ...         for chunk in response_instance:
        ...             executor.submit(print, chunk.text)

        >>> # this is optional as the model is designed with RAII in mind
        >>> del model
        ```
        ------------------------------------------------------------------------

        Args:
            pretrained (Path|str): the model either a huggingface model (str)
                                   or a path to a model (Path)

            config (BaseChatConfig): the config struct to use. can also be passed
                                 with the predict function for a one-off config

            image_processor_path (Optional[Path]): the path to the image processor
                                                    default is None

            timeout (Optional[int]): the time to wait for the model to load in
                                     seconds default is -1 (wait indefinitely)

        Raises:
            NotImplementedError:    incase a function is not implemented
            ModelNotFoundError:     if the model is not found
            ModelFailedToLoad:      if the model failed to load
            ModelTypeNotSupported:  if the model type is not supported
            ModelTookTooLongToLoad: if the model took too long to load
    """

    # ----------------------------------------------- public functions ----------------------------------------------- #

    def __init__(self,
                 pretrained: Path | Hub,
                 /,
                 image_processor_path: Optional[Path] = None ,
                 multi_model: Optional[bool]          = False, # this is to not check for clip in pretrained
                 timeout: Optional[int]               = -1   ) -> None:

        self.__model_name: str = ""
        self.__is_hub: bool = False

        self.__clip_model_path:  Optional[Llava15ChatHandler] = None
        self.__clip_path:        Optional[str]                = None
        self.__context:          ChatContext                  = ChatContext()

        if isinstance(pretrained, Hub):
            self.__is_hub = True
            self.__file_name: str = pretrained.file_name
            self.__model_name = pretrained.model_name

            if multi_model:
                self.__clip_model_path = None
                self.__clip_path = pretrained.clip_name

        elif isinstance(pretrained, Path):
            # set the path to the complete absolute path
            self.__model_name = str(pretrained.absolute())
            logger.info(f"Loading model: {self.__model_name}")

            if not os.path.exists(self.__model_name):
                raise ModelNotFoundError(f"Model not found: {self.__model_name}")

            if image_processor_path is not None:
                self.__clip_model_path = None
                self.__clip_path       = str(image_processor_path)

        else:
            raise ModelNotFoundError(f"Model not found: {pretrained}")

        self.__config:        Config  = Config
        self.__multi_model:     bool  = True if self.__clip_path is not None else False
        self.__timeout:          int  = timeout if timeout is not None else -1
        self.__is_model_loaded: bool  = True
        self.__model: Optional[Llama] = None
        
        # create a new thread to load the model asynchronously with concurrent.futures
        logger.info("starting model load")
        # wait asynchronously for the model to load
        try:
            self.__loaded_model = threading.Thread(target=self._load_model,
                                            daemon=True,
                                            name="load_model_thread")
            self.__loaded_model.start()
            logger.info("model load started")
        except TimeoutError:
            raise ModelTookTooLongToLoad(f"Model took too long to load: {self.__model_name}")

        except Exception as e:
            raise ModelFailedToLoad(f"Model failed to load: {self.__model_name} -> {e}")

        finally:
            logger.info("starting garbage collection")
            gc.collect() # collect garbage to free up memory
            logger.info("garbage collection done")
    # end                                                                                                     __init__ #

    def __del__(self) -> None:
        self._unload_model()
    # end                                                                                                      __del__ #

    def predict(self, request: ChatRequest) -> Iterator[ChatResponse]:
        """ Generates predictions based on the given chat request using the loaded model.
            Yields chat responses as they are generated.

            Args:
                request (ChatRequest): The chat request containing text and images.

            Returns:
                Iterator[ChatResponse]: An iterator of chat responses in web compatible format.

            Raises:
                ModelFailedToLoad: If the model did not start loading or is unloaded.
                ModelTookTooLongToLoad: If the model took too long to load.
        """
        logger.info("Predicting")

        if self.__model is None:
            # threading.Thread(target=self.__loaded_model.join, daemon=True, kwargs={"timeout": self.__timeout if self.__timeout > 0 else None}).start()
            logger.warning("Waiting for model to load")

        if self.__is_model_loaded is False:
            raise ModelFailedToLoad("Model did not start loading or is unloaded")

        # time_counter: int = 0
        while self.__model is None:
            # time.sleep(1)
            # time_counter += 1
            #
            # if time_counter >= self.__timeout: # and self.__timeout > 0:
            #    self.__loaded_model.join(timeout=0.1)
            #    raise ModelTookTooLongToLoad("Model took too long to load")
            # FIXME this causes a segfault
            pass

        if self.__model is None:
            raise ModelFailedToLoad("Model failed to load")

        tokens_generated: int = 0
        partial_response: dict[str, Union[str, int, list[dict[str, str | dict[str, str]]]]] = {
            "content": "",
        }

        self.__context.append(
            text=request.text,
            base64_images=[
                f"{img_data.img_id}|data:image/png;base64,{img_data.base64_img}"
                for img_data in request.images
            ] if request.images else None
        )

        stream: Iterator[CreateChatCompletionStreamResponse] = self.__model.create_chat_completion(
            messages=self.__context.get_context(),

            max_tokens=None,
            temperature=request.temperature,
            top_k=request.top_k,
            top_p=request.top_p,
            seed=request.seed,
            stream=True,
        )

        logger.info(f"Got the following config for this request - "
                    f"temperature: {request.temperature}, "
                    f"top_k: {request.top_k}, "
                    f"top_p: {request.top_p}, "
                    f"seed: {request.seed} ")

        while True:
            try: response: ChatCompletionRequestMessage = next(stream)
            except IndexError:
                logger.error("Model failed to generate a response due to consuming more tokens then max_ctx tokens")
                return ChatResponse(
                    id="",
                    model="",
                    created=0,
                    index=0,
                    role=None,
                    content=None,
                    finish_reason="length"
                )
            
            response_choice: Optional[dict] = response["choices"][0]

            if not isinstance(response_choice, dict):
                continue

            if (role := str(dict(response_choice.get("delta")).get("role", ""))):
                partial_response["id"]      = response["id"]
                partial_response["model"]   = response["model"]
                partial_response["created"] = response["created"]
                partial_response["role"]    = role
                continue

            if (content := str(dict(response_choice.get("delta")).get("content", ""))):
                partial_response["content"] += content
                partial_response["finish_reason"] = (
                    "None"
                    if (finish_reason := str(response_choice["finish_reason"])) == "None"
                    else finish_reason
                )

            yield ChatResponse(
                id=partial_response["id"],
                model=partial_response["model"],
                created=partial_response["created"],
                role=partial_response["role"],

                index=int(str(response_choice["index"])),
                content=content,
                finish_reason=(
                    "None"
                    if (finish_reason := str(response_choice["finish_reason"])) == "None"
                    else finish_reason
                )
            ) #                                                                                             yield return
            
            if response_choice["finish_reason"] == "stop":
                self.__context.append(
                    role=str(partial_response["role"]),
                    text=str(partial_response["content"])
                )
                break
    # end                                                                                                      predict #

    def predict_batch(self, requests: list[ChatRequest]) -> list[ChatResponse]:
        """ Generates predictions based on the given chat requests using the loaded model.
            Returns a list of chat responses. This function predicts the responses in parallel.

            Args:
                requests (list[ChatRequest]): The chat requests containing text and images.

            Returns:
                list[ChatResponse]: A list of chat responses in web compatible format.

            Raises:
                ModelFailedToLoad: If the model did not start loading or is unloaded.
                ModelTookTooLongToLoad: If the model took too long to load.
        """
        raise NotImplementedError("predict_batch is not implemented")
    # end                                                                                                predict_batch #

    # -------------------------------------------------- properties -------------------------------------------------- #

    @property
    def is_loaded(self) -> bool:
        return self.__is_model_loaded
    # end                                                                                                    is_loaded #

    @property
    def model_name(self) -> str:
        return self.__model_name
    # end                                                                                                   model_name #

    @property
    def current_config(self) -> BaseChatConfig:
        return BaseChatConfig(
            max_images=self.__config.max_images,
            max_tokens=self.__config.max_tokens,
            keep_in_mem=self.__config.keep_in_mem
        )
    # end                                                                                               current_config #

    @property
    def multi_model(self) -> bool:
        return self.__multi_model
    # end                                                                                                  multi_model #

    @property
    def timeout(self) -> int:
        return self.__timeout
    # end                                                                                                      timeout #

    @timeout.setter
    def timeout(self, value: int) -> None:
        self.__timeout = value
    # end                                                                                               timeout.setter #

    @property
    def model_path(self) -> Path:
        return Path(self.__model_name)
    # end                                                                                                   model_path #

    @property
    def context(self) -> ChatContext:
        return self.__context

    # ----------------------------------------------- private functions ---------------------------------------------- #

    def _load_model(self) -> None:
        if self.__is_hub:
            if not os.path.exists(Path(os.getcwd(), "Server", "models")):
                os.makedirs(Path(os.getcwd(), "Server", "models"), exist_ok=True)

            if self.__multi_model:
                self.__clip_model_path = MoondreamChatHandler.from_pretrained(
                    repo_id   = self.__model_name,
                    filename  = self.__clip_path,
                    local_dir = Path(os.getcwd(), "Server", "models"),
                    verbose   = False,
                )

            self.__model     = Llama.from_pretrained(
                repo_id      = self.__model_name,
                filename     = self.__file_name,
                chat_handler = self.__clip_model_path if self.__clip_model_path is not None else None,
                local_dir    = Path(os.getcwd(), "Server", "models"),

                use_mlock    = self.__config.keep_in_mem,
                n_ctx        = self.__config.max_tokens,
                n_gpu_layers = -1,
                verbose      = False,
            )
        else:
            if self.__multi_model and self.__clip_path is not None:
                self.__clip_model_path = Llava15ChatHandler(
                    clip_model_path    = self.__clip_path,
                    verbose            = False
                )

            self.__model     = Llama(
                model_path   = self.__model_name,
                chat_handler = self.__clip_model_path if self.__clip_model_path is not None else None,

                use_mlock    = self.__config.keep_in_mem,
                n_ctx        = self.__config.max_tokens,
                n_gpu_layers = -1,
                verbose      = False,
            )

        if self.__model is None:
            self.__is_model_loaded = False
            raise ModelFailedToLoad("Model failed to load")
    # end                                                                                                  _load_model #

    def _unload_model(self) -> None:
        logger.info("Unloading model")
        del self.__model
        gc.collect()

        logger.info("Model unloaded")
        self.__is_model_loaded = False
        self.__model = None # set the model to None to prevent further use
    # end                                                                                                _unload_model #
# end                                                                                                        LoadModel #
