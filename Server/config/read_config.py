# ------------------------------------------------- regular imports -------------------------------------------------- #

import toml
import logging

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

    @classmethod
    def load(cls, file_path):
        with open(file_path, 'r') as f:
            config_data = toml.load(f)

        cls.keep_in_mem     = dict(config_data.get('config', {})).get('keep_in_mem',     False     )
        cls.max_images      = dict(config_data.get('config', {})).get('max_images',      5         )
        cls.max_tokens      = dict(config_data.get('config', {})).get('max_tokens',      512       )
        cls.huggingface_key = dict(config_data.get('config', {})).get('huggingface_key', ""        )
        
        cls.server_ip       = dict(config_data.get('server', {})).get('ip',              "0.0.0.0" )
        cls.server_password = dict(config_data.get('server', {})).get('password',        "password")
        cls.server_port     = dict(config_data.get('server', {})).get('port',            8282      )
        
        logger.info(f"Config loaded from {file_path}")
        
        logger.debug(f"Loaded config - keep_in_mem: {cls.keep_in_mem}, max_images: "
                     f"{cls.max_images}, max_tokens: {cls.max_tokens}, "
                     f"huggingface_key: {cls.huggingface_key}"
                     f"server_ip: {cls.server_ip}, server_password: {cls.server_password}, "
                     f"server_port: {cls.server_port}")
    # end                                                                                                         load #
# end                                                                                                           Config #