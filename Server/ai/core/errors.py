# ------------------------------------------------------ errors ------------------------------------------------------ #

class ModelNotFoundError(Exception):
    pass

class ModelFailedToLoad(Exception):
    pass

class ModelTypeNotSupported(Exception):
    pass

class ModelTookTooLongToLoad(Exception):
    pass
