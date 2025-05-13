# ------------------------------------------------- regular imports -------------------------------------------------- #

import toml
import logging
import os
from pathlib import Path

# -------------------------------------------------- set up logging -------------------------------------------------- #

logger: logging.Logger = logging.getLogger("rich")

# ------------------------------------------------------ config ------------------------------------------------------ #

class Config:
    # [config]
    keep_in_mem:     bool = False
    max_images:      int  = 5
    max_tokens:      int  = 512
    huggingface_key: str  = ""
    
    # [server]
    server_ip:       str  = "0.0.0.0"
    server_password: str  = "password"
    server_port:     int  = 8282
    
    # [logging]
    log_level:       str  = "info"
    log_to_file:     bool = False
    log_file:        str  = "voxai_server.log"

    @classmethod
    def load(cls, file_path):
        if not os.path.exists(file_path):
            logger.warning(f"Config file not found: {file_path}. Using default configuration.")
            return
        
        with open(file_path, 'r') as f:
            config_data = toml.load(f)

        # Load [config] section
        config_section = dict(config_data.get('config', {}))
        cls.keep_in_mem     = config_section.get('keep_in_mem', False)
        cls.max_images      = config_section.get('max_images', 5)
        cls.max_tokens      = config_section.get('max_tokens', 512)
        cls.huggingface_key = config_section.get('huggingface_key', "")
        
        # Load [server] section
        server_section = dict(config_data.get('server', {}))
        cls.server_ip       = server_section.get('ip', "0.0.0.0")
        cls.server_password = server_section.get('password', "password")
        cls.server_port     = server_section.get('port', 8282)
        
        # Load [logging] section
        logging_section = dict(config_data.get('logging', {}))
        cls.log_level       = logging_section.get('level', "info").lower()
        cls.log_to_file     = logging_section.get('log_to_file', False)
        cls.log_file        = logging_section.get('log_file', "voxai_server.log")
        
        # Configure logging based on settings
        cls.configure_logging()
        
        logger.info(f"Config loaded from {file_path}")
        
        logger.debug(f"Loaded config - keep_in_mem: {cls.keep_in_mem}, max_images: "
                    f"{cls.max_images}, max_tokens: {cls.max_tokens}, "
                    f"huggingface_key: {cls.huggingface_key}, "
                    f"server_ip: {cls.server_ip}, server_password: *****, "
                    f"server_port: {cls.server_port}, "
                    f"log_level: {cls.log_level}, log_to_file: {cls.log_to_file}, "
                    f"log_file: {cls.log_file}")
    
    @classmethod
    def configure_logging(cls):
        log_level = getattr(logging, cls.log_level.upper(), logging.INFO)
        
        handlers = []
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Always add console handler
        from rich.logging import RichHandler
        console_handler = RichHandler()
        handlers.append(console_handler)
        
        # Add file handler if enabled
        if cls.log_to_file:
            try:
                file_handler = logging.FileHandler(cls.log_file)
                file_handler.setFormatter(formatter)
                handlers.append(file_handler)
            except Exception as e:
                logger.error(f"Failed to set up file logging: {e}")
        
        # Configure root logger
        logging.basicConfig(
            level=log_level,
            format="%(message)s",
            datefmt="[%X]",
            handlers=handlers
        )
        
        # Set levels for specific loggers
        logging.getLogger("uvicorn").setLevel(log_level)
        logging.getLogger("fastapi").setLevel(log_level)
        
        logger.debug(f"Logging configured with level: {cls.log_level.upper()}")
# end                                                                                                           Config #