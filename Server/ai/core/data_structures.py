# ------------------------------------------------- regular imports -------------------------------------------------- #

import os
import sys
import logging

from typing   import Literal, Optional
from pydantic import BaseModel, Field

# -------------------------------------------------- set up logging -------------------------------------------------- #

logger: logging.Logger = logging.getLogger("rich")

# ---------------------------------------------------- models -------------------------------------------------------- #

class AudioData(BaseModel):
    ...
# end                                                                                                        AudioData #

class ImageData(BaseModel):
    img_id:     str = Field(..., description="the unique identifier for the image")
    base64_img: str = Field(..., description="the base64 for the image")
# end                                                                                                        ImageData #

class TranscribedText(BaseModel):
    ...
# end                                                                                                  TranscribedText #

class TrainingRequest(BaseModel):
    ...
# end                                                                                                  TrainingRequest #

class BaseChatConfig(BaseModel):
        """ ChatConfig
            ChatConfig - represents the configuration for chat
    
            Args:
                max_images (int): the maximum number of images to return
                max_tokens (int): the maximum number of tokens to return
                temperature (float): the temperature for sampling
                top_k (int): the top k tokens to sample from
                top_p (float): the top p tokens to sample from
                seed (int): the random seed for sampling
        """

        max_images:  int   = Field(..., description="the maximum number of images to return")
        max_tokens:  int   = Field(..., description="the maximum number of tokens to return")
        keep_in_mem: bool  = Field(..., description="whether to keep the model in memory")
# end                                                                                                       ChatConfig #

class ChatRequest(BaseModel):
    text:        str   = Field(..., description="the text to use for chat")
    top_k:       int   = Field(40 , description="the top k tokens to sample from")
    top_p:       float = Field(1.0, description="the top p tokens to sample from")
    min_p:       float = Field(0.0, description="the minimum p tokens to sample from")
    temperature: float = Field(0.7, description="the temperature for sampling")
    
    seed:        Optional[int]             = Field(None, description="the random seed for sampling")
    images:      Optional[list[ImageData]] = Field(None, description="the images to use for chat")
# end                                                                                                      ChatRequest #

class ChatResponse(BaseModel):
    id:            str           = Field(..., description="the unique identifier for the response")
    model:         str           = Field(..., description="the model used to generate the response")
    created:       int           = Field(..., description="the unix time the response was created")
    index:         int           = Field(..., description="the index of the response")
    role:          Optional[str] = Field(..., description="the role of the response 'system', 'user' or 'assistant'")
    content:       Optional[str] = Field(..., description="the content of the response")
    finish_reason: Optional[str] = Field(..., description="the reason the response was finished 'none', "
                                                          "'length', 'function_call'")
# end                                                                                                     ChatResponse #



# ----------------------------------------------------- utils -------------------------------------------------------- #
