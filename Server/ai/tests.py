# ------------------------------------------------- regular imports -------------------------------------------------- #

import os
import sys
from   typing import Any, Callable

# -------------------------------------------------- local imports --------------------------------------------------- #

from .tech_enum           import TechStackEnum                                                             # type:ignore
from .model_loader                  import GITImageProcessor                                                         # type:ignore
from .utils               import UTILS                                                                     # type:ignore
from .utils               import HandleJson                                                                # type:ignore

# -------------------------------------------------- set up logging -------------------------------------------------- #

import  logging
logger: logging.Logger = logging.getLogger("rich")

# --------------------------------------------------- TESTS ---------------------------------------------------------- #

class RunTests: # .................................................................................................... #
    __all_tests: list[Callable[[Any], None]]


    def __init__(self) -> None: # .................................................................................... #
        
        """ RunTests.__init__
            __init__ - initializes the tests to run by calling the `next()` method
            
            ```python
            tests = RunTests()
            tests.next() # runs _1
            tests.next() # runs _2 if implemented else logs an error (does not raise an exception)
            ```
            
            Returns:
                None
        """
        
        logger.info("initializing tests")

        self.__current_test: int = 0
        RunTests.__all_tests = [
            getattr(RunTests, func)
            for func in dir(self)
            if (    func    .startswith("_")
                and func[1] .isdigit()
                and callable(getattr(self, func))
            )
        ]

        RunTests.__all_tests.sort(key=lambda x: int(x.__name__[1:])) # sort tests by number 1..n

        logger.debug(f"all tests: {RunTests.__all_tests}")
    # end ............................................. RunTests ......................................... -> __init__ #

    def next(self, *args, **kwargs) -> None: # ....................................................................... #
        
        """ RunTests.next
            next - runs the next test in the list of tests
            
            Args:
                *args: any arguments to pass to the test
                **kwargs: any keyword arguments to pass to the test
                
            Returns:
                None
        """
        
        if self.__current_test < len(RunTests.__all_tests):
            RunTests.__all_tests[self.__current_test](self, *args, **kwargs)
            self.__current_test += 1
        else:
            logger.error("all tests completed")
    # end ............................................. RunTests ............................................. -> next #


    def _1(self) -> None: # .......................................................................................... #
        
        """ RunTests.test_1
            test_1 - tests if requirement.txt and llama_cpp is installed
            
            Raises:
                ImportError: if torch is not installed
                ImportError: if llama_cpp is not installed
                
            Returns:
                None
        """
        
        logger.debug("test 1.1 - testing if torch is installed, if this fails then is requirement.txt installed?")
        try:
            import torch
        except ImportError:
            logger.error("requirement.txt is not installed auto running 'python -m venv .venv' "
                         "and"
                         " '.venv/bin/python3 -m pip install -r requirements.txt'")
            os.system(f"{sys.executable} -m venv .venv")
            
            if not os.path.exists(os.path.join(os.getcwd(), ".venv", "bin", "python3")):
                logger.error("failed to create virtual environment run commands manually")
                return #                                                                                        return #
            
            os.system(f"{os.path.join(os.getcwd(), ".venv", "bin", "python3")} -m pip install -r requirements.txt")
            logger.info("successfully installed requirements.txt run 'python -m venv .venv'"
                "to activate the virtual environment")
            
            sys.exit(0)
        
        logger.debug("test 1.2 - testing if llama_cpp is installed, if not this "
                     "test will error and auto install it based on the platform")
        
        import llama_cpp
        
        
    # end ............................................. RunTests ........................................... -> test_1 #

    def _2(self, data_path: str) -> None: # .......................................................................... #
        raise NotImplementedError("test_2 is not yet implemented")
    # end ............................................. RunTests ........................................... -> test_2 #

    def _3(self, GIT_inst: GITImageProcessor) -> None: # ............................................................. #
        raise NotImplementedError("test_3 is not yet implemented")
    # end ............................................. RunTests ........................................... -> test_3 #
