# ------------------------------------------------- regular imports -------------------------------------------------- #

import os
import sys
from   typing import Callable, NoReturn, final

# -------------------------------------------------- set up logging -------------------------------------------------- #

import  logging
logger: logging.Logger = logging.getLogger("rich")

# ----------------------------------------------------- install ------------------------------------------------------ #

PYTHON_VENV_PATH: str = os.path.join(os.getcwd(), ".venv", "bin", "python3")

class installer:
    @staticmethod
    def install(what: str | int) -> NoReturn:

        """ installer.install
            install - installs the specified package or packages

            Args:
                what (str | int): the package or packages to install

            Returns:
                sys.exit
        """

        install_functions: dict[tuple[str, int], Callable[[], None]] = {
            ("requirements", 100): installer.install_requirements,
            ("llama_cpp",    200): installer.install_inference,
            ("whispercpp",   300): installer.install_whispercpp
        }

        if isinstance(what, str):
            installer.handle_what_as_str(what, install_functions)

        elif isinstance(what, int):
            installer.handle_what_as_int(what, install_functions)

        logger.warning("re-run this script to install other packages if needed")
        sys.exit(0) #                                                                                             exit #
    # end                                                                                                      install #

    @staticmethod
    def handle_what_as_int(what: int, /, passed_functions: dict[tuple[str, int], Callable[[], None]]) -> None:
        """ installer.handle_what_as_int
            handle_what_as_int - handles the case where the `what` argument is an integer and calls
                                 the appropriate function from the `passed_functions` dictionary and
                                 logs an error if the function does not exist

            Args:
                what (int): the integer to match
                passed_functions (dict[tuple[str, int], Callable[[], None]]): the functions to match against

            Returns:
                None
        """

        functions: dict[int, Callable[[], None]] = {key[1]: value for key, value in passed_functions.items()}

        if what in functions:
            functions[what]()
        else:
            logger.error(f"attempted to install {what} but no such function exists")
    # end                                                                                           handle_what_as_int #

    @staticmethod
    def handle_what_as_str(what: str, /, passed_functions: dict[tuple[str, int], Callable[[], None]]) -> None:

        """ installer.handle_what_as_str
            handle_what_as_str - handles the case where the `what` argument is a string and calls
                                 the appropriate function from the `passed_functions` dictionary and
                                 logs an error if the function does not exist

            Args:
                what (str): the string to match
                passed_functions (dict[tuple[str, int], Callable[[], None]]): the functions to match against

            Returns:
                None
        """

        functions: dict[str, Callable[[], None]] = {key[0]: value for key, value in passed_functions.items()}

        if (what := what.lower()) in functions:
            functions[what]()
        else:
            logger.error(f"attempted to install {what} but no such function exists")
    # end                                                                                           handle_what_as_str #

    @staticmethod
    def install_whispercpp() -> None:
            
            """ installer.install_whispercpp
                install_whispercpp - installs the whispercpp package with the appropriate settings and
                                     environment variables
    
                Returns:
                    None
            """
    
            os.system(f"{sys.executable} -m venv .venv")
            
    
            if not os.path.exists(PYTHON_VENV_PATH):
                logger.error("failed to create virtual environment run commands manually")
                return #                                                                                        return #
            
            os.system(f"{PYTHON_VENV_PATH} -m pip install -U pip setuptools wheel")
            
            # add PYTHON_VENV_PATH to current shell environment
            if sys.platform == "win32":
                os.system(f"set PYTHON_BIN_PATH={PYTHON_VENV_PATH}")
            else:
                os.system(f"export PYTHON_BIN_PATH={PYTHON_VENV_PATH}")
            
            # FIXME: use AIWintermuteAI/whispercpp once wheel is available
            os.system(f"{PYTHON_VENV_PATH} -m pip install whispercpp")
            logger.info("successfully installed whispercpp run 'python -m venv .venv'")
    # end                                                                                           install_whispercpp #
            
    @staticmethod
    def install_requirements() -> None:

        """ installer.install_requirements
            install_requirements - installs all the requirements form the requirements.txt file

            Returns:
                None
        """

        os.system(f"{sys.executable} -m venv .venv")

        if not os.path.exists(PYTHON_VENV_PATH):
            logger.error("failed to create virtual environment run commands manually")
            return #                                                                                            return #

        os.system(f"{PYTHON_VENV_PATH} -m pip install -r requirements.txt")
        logger.info("successfully installed requirements.txt run 'python -m venv .venv'")
    # end                                                                                         install_requirements #

    @staticmethod
    def install_inference() -> None:

        """ installer.install_inference
            install_inference - installs the llama_cpp package with the appropriate settings and
                                environment variables

            Returns:
                None
        """

        if installer.check_prebuilt_wheel_support():
            logger.info("prebuilt wheel support detected. Attempting to install prebuilt wheel.")
            installer.install_prebuilt_wheel()

        else:
            logger.info("no prebuilt wheel support detected. Building from source.")
            installer.build_from_source()
    # end                                                                                            install_inference #

    @staticmethod
    def check_prebuilt_wheel_support() -> bool:

        """ installer.check_prebuilt_wheel_support
            check_prebuilt_wheel_support - checks if the system supports a prebuilt wheel installation

            Returns:
                bool: True if supported, False otherwise
        """

        logger.info("checking for prebuilt wheel support...")

        if installer.is_arm64_mac() and installer.python_version_supported():
            logger.info("macOS detected and Python version supported for prebuilt wheel.")
            return True #                                                                                       return #

        if installer.has_cuda() and installer.python_version_supported():
            logger.info("CUDA detected and Python version supported for prebuilt wheel.")
            return True #                                                                                       return #

        if installer.is_cpu() and installer.python_version_supported():
            logger.info("CPU detected and Python version supported for prebuilt wheel.")
            return True #                                                                                       return #

        logger.warning("no prebuilt wheel support detected.")
        return False #                                                                                          return #
    # end                                                                                 check_prebuilt_wheel_support #

    @staticmethod
    def has_cuda() -> bool:

        """ installer.has_cuda
            has_cuda - checks if the system has CUDA installed

            Returns:
                bool: True if CUDA is installed, False otherwise
        """

        try:
            result: int = os.system("nvcc --version")

            if result == 0:
                logger.info("CUDA detected.")
                return True #                                                                                   return #

            logger.warning("CUDA not detected.")
            return False #                                                                                      return #

        except FileNotFoundError:
            logger.error("CUDA check failed, nvcc not found.")
            return False #                                                                                      return #
    # end                                                                                                     has_cuda #

    @staticmethod
    def python_version_supported() -> bool:

        """ installer.python_version_supported
            python_version_supported - checks if the Python version is supported

            Returns:
                bool: True if supported, False otherwise
        """

        version_supported: bool = sys.version_info >= (3, 10)

        logger.info(f"python version {'supported' if version_supported else 'not supported'}: {sys.version}")
        return version_supported #                                                                              return #
    # end                                                                                     python_version_supported #

    @staticmethod
    def is_arm64_mac() -> bool:

        """ installer.is_arm64_mac
            is_arm64_mac - checks if the system is running macOS and if its arm64 (apple silicon)

            Returns:
                bool: True if running macOS, False otherwise
        """

        is_arm64_mac: bool = sys.platform == "darwin" and os.uname().machine == "arm64"

        logger.info(f"system is {'macOS' if is_arm64_mac else 'not macOS'}: {sys.platform}")
        return is_arm64_mac #                                                                                   return #
    # end                                                                                                 is_arm64_mac #

    @staticmethod
    def is_cpu() -> bool:

        """ installer.is_cpu
            is_cpu - checks if the system is using a CPU

            Returns:
                bool: True if using a CPU, False otherwise
        """

        is_cpu: bool = not installer.has_cuda() and not installer.is_arm64_mac()

        logger.info(f"system is {'CPU' if is_cpu else 'not CPU'} based.")
        return is_cpu #                                                                                         return #
    # end                                                                                                       is_cpu #

    @staticmethod
    def install_prebuilt_wheel() -> None:

        """ installer.install_prebuilt_wheel
            install_prebuilt_wheel - installs the prebuilt wheel if supported

            Returns:
                None
        """

        logger.info("installing prebuilt wheel...")

        if installer.is_arm64_mac():
            logger.info("installing prebuilt wheel for macOS Metal support.")
            os.system(f"{PYTHON_VENV_PATH} -m pip install llama-cpp-python "
                       "--extra-index-url https://abetlen.github.io/llama-cpp-python/whl/metal")

        elif installer.has_cuda():
            cuda_version: str = installer.get_cuda_version()

            logger.info(f"installing prebuilt wheel for CUDA version: {cuda_version}")
            os.system(f"{PYTHON_VENV_PATH} -m pip install llama-cpp-python "
                      f"--extra-index-url https://abetlen.github.io/llama-cpp-python/whl/{cuda_version}")

        else:
            logger.info("installing prebuilt wheel for CPU support.")
            os.system(f"{PYTHON_VENV_PATH} -m pip install llama-cpp-python "
                       "--extra-index-url https://abetlen.github.io/llama-cpp-python/whl/cpu")
    # end                                                                                       install_prebuilt_wheel #

    @staticmethod
    def get_cuda_version() -> str:

        """ installer.get_cuda_version
            get_cuda_version - retrieves the installed CUDA version

            Returns:
                str: the CUDA version in the required format
        """

        cuda_version_map: dict[str, str] = {
            "12.1": "cu121",
            "12.2": "cu122",
            "12.3": "cu123",
            "12.4": "cu124"
        }

        try:
            result: str = os.popen("nvcc --version | grep release | awk '{print $6}' | awk -F',' '{print $1}'")        \
                            .read()                                                                                    \
                            .strip()

            cuda_version: str = cuda_version_map.get(result, "cu121")

            logger.info(f"detected CUDA version: {result}, mapped to: {cuda_version}")
            return cuda_version #                                                                               return #

        except Exception as e:
            logger.error(f"failed to detect CUDA version: {e}")
            return "cu121" #                                                                                    return #
    # end                                                                                             get_cuda_version #

    @staticmethod
    def build_from_source() -> None:

        """ installer.build_from_source
            build_from_source - builds llama_cpp from source with appropriate environment variables

            Returns:
                None
        """

        cmake_args: str = installer.get_cmake_args()

        logger.info(f"building from source with CMake arguments: {cmake_args}")
        os.system(f"CMAKE_ARGS=\"{cmake_args}\" pip install llama-cpp-python --verbose")
    # end                                                                                            build_from_source #

    @staticmethod
    def get_cmake_args() -> str:

        """ installer.get_cmake_args
            get_cmake_args - constructs the appropriate CMake arguments for building from source

            Returns:
                str: the CMake arguments
        """

        cmake_args: list[str] = []

        if installer.is_arm64_mac():
            cmake_args.append("-DLLAMA_METAL=on")

        if installer.has_cuda():
            cmake_args.append("-DLLAMA_CUDA=on")

        if installer.is_cpu():
            cmake_args.append("-DLLAMA_BLAS=ON -DLLAMA_BLAS_VENDOR=OpenBLAS")

        cmake_args_str = " ".join(cmake_args)

        logger.info(f"constructed CMake arguments: {cmake_args_str}")
        return cmake_args_str #                                                                                 return #
    # end                                                                                               get_cmake_args #
# end                                                                                                        installer #

@final
class prelude(installer):

    """ prelude
        prelude - this is the final class that extends all the other classes required for the prelude
    """

    def __init__(self) -> None:

        """ prelude.__init__
            __init__ - raises an exception if this class is instantiated

            Raises:
                Exception: This class is not meant to be instantiated.
        """

        raise Exception("This class is not meant to be instantiated.")
    # end                                               prelude                                               __init__ #
# end                                                                                                          prelude #
