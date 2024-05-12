import subprocess
import rich
import logging

logger = logging.getLogger()

def check_surreal_installed() -> bool:
    try:
        import surrealdb
        subprocess.run(["surreal", "help"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        return True
    except (ImportError, FileNotFoundError):
        return False
    
def _test() -> None:
    logger.info("running warmup tests")
    logger.debug("checking if surreal is installed (module and command line)")
    assert check_surreal_installed(), "surreal is not installed"
    logger.debug("surreal is installed")
    
