# ------------------------------------------------- regular imports -------------------------------------------------- #

import json
import logging

from typing                    import Optional, Union
from Server.config.read_config import Config

# -------------------------------------------------- set up logging -------------------------------------------------- #

import  logging

logger: logging.Logger = logging.getLogger("rich")

# ----------------------------------------------------- context ------------------------------------------------------ #

class SingleChatContent:
    """
        This class will contain the context for a single chat. It includes the following:
            - the role of the chat
            - the content of the chat
            - a flag to check if text has been added to the chat

        Attributes:
            __text_added (bool): Flag indicating if text has been added.
            role (str): The role of the chat, e.g., 'user' or 'system'.
            content (list[dict[str, str | dict[str, str]]]): list to store the chat content.
    """

    def __init__(self,
                 /,
                 role: str = "user",
                 text: Optional[str] = None,
                 base64_images: Optional[list[str]] = None) -> None:
        """ Initializes the SingleChatContent with the given role, text, and base64_images.

            Args:
                role (str): The role of the chat. Default is 'user'.
                text (Optional[str]): The text content to add. Default is None.
                base64_images (Optional[list[str]]): list of base64 encoded images. Default is None.
        """
        self.__text_added: bool = False
        self.role: str = role
        self.content: list[dict[str, Union[str, dict[str, str]]]] | str = []

        if text:
            self.add_text(text)

        if base64_images:
            self.add_images(base64_images)

        logger.debug(f"Initialized SingleChatContent with role={role}, text={text}, base64_images="
                      + ' '.join(
                        [
                            f"data:image/png;base64,{str(len(bytes(base64_uri.split(',')[1], 'utf-8')))}bytes"
                            for base64_uri in base64_images
                        ]
                    ) if base64_images else 'None')
        # end                                                                                                 __init__ #

    def add_text(self, text: str) -> None:
        """
            Adds text to the chat content. Logs an error if text has already been added.

            Args:
                text (str): The text content to add.
        """
        if self.__text_added:
            logger.error("Text has already been submitted to this context, "
                         f"current text: {[txt for txt in self.content if txt['type'] == 'text'][0]['text']}")
            return

        if self.role == "user" and isinstance(self.content, list):
            self.content.append(
                {
                    "type": "text",
                    "text": text
                }
            )

        else:
            self.content = text

        self.__text_added = True
        logger.debug(f"Added text: {text}")
    # end                                                                                                     add_text #

    def is_image_added(self, base64_uri: str) -> bool:
        """
            Checks if an image has already been added to the chat content.

            Args:
                base64_uri (str): The base64 URI of the image to check.

            Returns:
                bool: True if the image has been added, False otherwise.
        """
        for content in self.content:
            image_url = content.get("image_url") if content["type"] == "image_url" else None

            if isinstance(image_url, dict) and image_url.get("url") == base64_uri:
                logger.error("Image has already been submitted to this context, omitting...")
                return True

        return False
    # end                                                                                               is_image_added #

    def add_image(self, base64: str) -> None: # base64_uri = img10|data:image/png;base64,{base64_data}
        """
            Adds an image to the chat content. Logs an error if the image is not in the correct format or has already been added.

            Args:
                base64 (str): The base64 encoded image with a tag.
        """
        if "|" not in base64 or not (tag := base64.split("|")[0].lstrip()):
            logger.error("Image is not in the correct format, omitting...")
            return

        if not (base64_uri := base64.split("|")[1].lstrip()) or not base64_uri.startswith("data:image/png;base64,"):
            logger.error("Image is not in the correct format, omitting...")
            return

        if self.is_image_added(base64_uri):
            return

        self.content.extend([
            {
                "type": "text",
                "text": f"tag={tag}"
            },
            {
                "type": "image_url",
                "image_url": {
                    "url": base64_uri
                }
            }
        ])

        logger.debug(
            f"Added image with tag={tag} and base64_uri="
            f"data:image/png;base64,{str(len(bytes(base64_uri.split(',')[1], 'utf-8')))}bytes")
    # end                                                                                                    add_image #

    def add_images(self, base64: list[str]) -> None:
        """
        Adds multiple images to the chat content.

        Args:
            base64 (list[str]): list of base64 encoded images with tags.
        """
        for base64_image in base64:
            self.add_image(base64_image)
        logger.debug(f"Added multiple images: " + ' '.join(
            [
                f"data:image/png;base64,{str(len(bytes(base64_uri.split(',')[1], 'utf-8')))}bytes"
                for base64_uri in base64
            ]
        ))
    # end                                                                                                   add_images #

    def get_content(self) -> dict[str, Union[str, list[dict[str, Union[str, dict[str, str]]]]]]:
        """
        Retrieves the chat content.

        Returns:
            dict[str, str | list[dict[str, str | dict[str, str]]]]: The chat content.
        """
        logger.debug("Retrieved chat content.")
        return {
            "role":    self.role,
            "content": self.content
        }
    # end                                                                                            SingleChatContext #
# end                                                                                                SingleChatContent #

class ChatContext:
    """ Manages the chat context for an local llm.
        Provides methods to append new content, retrieve the current context, and save/load context from a file.

        Attributes:
            base_prompt (dict[str, str]): The initial system prompt for the assistant.
            contexts (list[SingleChatContent]): A list to store chat content.
            total_images (int): The total number of images in the context.
    """
    base_prompt: dict[str, str] = {
        "role": "system",
        "content": (
            "you are an intelligent assistant designed to help students with their "
            "lectures. You can respond to student queries about lecture content, provide "
            "explanations using relevant images from your memory, and assist with topics "
            "by analyzing textbook images uploaded by students. Use the combined audio "
            "and visual data to give accurate, contextually appropriate answers, "
            "enhancing the students' learning experience. All your responses should be "
            "in the form of Markdown text"
        )
    }

    def __init__(self) -> None:
        """ Initializes the ChatContext with the base system prompt. """
        self.contexts: list[SingleChatContent] = [
            SingleChatContent(
                ChatContext.base_prompt["role"],
                ChatContext.base_prompt["content"]
            )
        ]
        self.total_images: int = 0

        logger.debug("Initialized ChatContext with base system prompt.")
    # end                                                                                                     __init__ #

    def append(
        self,
        /,
        role: str = "user",
        text: Optional[str] = None,
        base64_images: Optional[list[str]] = None
    ) -> None:
        """ Appends new content to the chat context.

            Args:
                role (str): The role of the content, e.g., 'user', 'system' or 'assistant'. Default is 'user'.
                text (Optional[str]): The text content to append.
                base64_images (Optional[list[str]]): list of base64 encoded images.
        """
        self.total_images += len(base64_images) if base64_images else 0
        if self.total_images > Config.max_images:
            logger.error(
                f"Cannot add more than {Config.max_images} images to the context, omitting..."
            )

        self.contexts.append(
            SingleChatContent(
                role,
                text,
                (
                    base64_images
                    if self.total_images <= Config.max_images
                    else None
                )
            )
        )

        logger.debug(
            f"Appended new content: role={role}, text={text}, base64_images="
            + ' '.join(
                [
                    f"data:image/png;base64,{str(len(bytes(base64_uri.split(',')[1], 'utf-8')))}bytes"
                    for base64_uri in base64_images
                ]
            ) if base64_images and self.total_images <= Config.max_images else 'None')

    # end                                                                                                  add_context #

    def get_context(self) -> list[dict[str, Union[str, list[dict[str, Union[str, dict[str, str]]]]]]]:
        """ Retrieves the current chat context.

            Returns:
                list[dict[str, str | list[dict[str, str | dict[str, str]]]]]: The current chat context.
        """
        context = [context.get_content() for context in self.contexts]
        logger.debug("Retrieved current chat context.")
        return context
    # end                                                                                                  get_context #

    # TODO: add edit context function

    def save_context(self, filepath: str = "context.json") -> None:
        """ Saves the current chat context to a file.

            Args:
                filepath (str): The path to the file where the context will be saved. Default is 'context.json'.
        """
        with open(filepath, "w") as file:
            json.dump(self.get_context(), file, indent=4)
        logger.info(f"Context saved to {filepath}")
        # FIXME: modify to use a database
    # end                                                                                                 save_context #

    def load_context(self, filepath: str = "context.json") -> None:
        """ Loads the chat context from a file.

            Args:
                filepath (str): The path to the file from which the context will be loaded. Default is 'context.json'.
        """
        with open(filepath, "r") as file:
            self.contexts = [SingleChatContent(context["role"], context["content"]) for context in json.load(file)]
        logger.info(f"Context loaded from {filepath}")
        # FIXME: modify to use a database
    # end                                                                                                 load_context #

    def __repr__(self) -> str:
        """ Returns a string representation of the chat context.

            Returns:
                str: The string representation of the chat context with image URLs replaced by their byte size.
        """
        modified_content: str = "\n" + json.dumps(self.get_context(), indent=4) + "\n"

        # remove the image urls from the string and replace them with how many bytes the base64 is
        for content in self.get_context():
            if isinstance(content, list):
                for chat in content["content"]:
                    if chat["type"] == "image_url":  # type:ignore
                        base64 = chat["image_url"]["url"]  # type:ignore
                        modified_content = modified_content.replace(
                            base64,
                            f"data:image/png;base64,{str(len(bytes(base64.split(',')[1], 'utf-8')))}bytes",
                        )

        logger.debug("Generated string representation of the chat context.")
        return modified_content
    # end                                                                                                     __repr__ #

    def __str__(self) -> str:
        """
            Returns a string representation of the chat context.

            Returns:
                str: The string representation of the chat context.
        """
        return self.__repr__()
    # end                                                                                                      __str__ #
# end                                                                                                      ChatContext #
