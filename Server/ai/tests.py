# ------------------------------------------------- regular imports -------------------------------------------------- #

import os
import sys
from   typing import Any, Callable

# -------------------------------------------------- local imports --------------------------------------------------- #

from .prelude import prelude

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

    def next(self, *args, **kwargs) -> None | BaseException: # ....................................................... #
        
        """ RunTests.next
            next - runs the next test in the list of tests
            
            Args:
                *args: any arguments to pass to the test
                **kwargs: any keyword arguments to pass to the test
                
            Returns:
                None | BaseException - if the test raises an exception it will be returned
        """
        
        if self.__current_test < len(RunTests.__all_tests):
            result: None | BaseException = RunTests.__all_tests[self.__current_test](self, *args, **kwargs)
            
            self.__current_test += 1
            return result #                                                                                       return
        
        else:
            logger.error("all tests completed")
            
        return None #                                                                                             return
    # end ............................................. RunTests ............................................. -> next #

    def _2(self) -> None | ImportError: # ............................................................................ #
        
        """ RunTests.test_1
            test_1 - tests if requirement.txt and llama_cpp is installed
            
            Raises:
                ImportError: if torch is not installed
                ImportError: if llama_cpp is not installed
                
            Returns:
                None | ImportError - if llama_cpp is not installed
        """
        
        logger.debug("test 1.1 - testing if torch is installed, if this fails then is requirement.txt installed?")
        try:
            import torch
        except ImportError:
            logger.error("requirement.txt is not installed auto running 'python -m venv .venv' "
                         "and"
                         " '.venv/bin/python3 -m pip install -r requirements.txt'")
            
            return ImportError("torch") #                                                                         return
        
        logger.debug("test 1.2 - testing if llama_cpp is installed, if not this "
                     "test will error and auto install it based on the platform")
        try:
            import llama_cpp
        
        except ImportError:
            logger.error("llama_cpp is not installed auto installing it")
            return ImportError("llama_cpp") #                                                                     return

        logger.debug("test 1.3 - testing if whispercpp is installed, if not this "
                     "test will error and auto install it based on the platform")
        try:
            import whispercpp
        
        except ImportError:
            logger.error("whispercpp is not installed auto installing it")
            return ImportError("whispercpp") #                                                                    return
        
        return None #                                                                                             return
    # end ............................................. RunTests ........................................... -> test_1 #

    def _1(self) -> None: # .......................................................................................... #
        # check if the dir is in VoxAI/Server or VoxAI, if its in Server then we need to move up one dir
        if os.path.basename(os.getcwd()) == "Server":
            logger.error("please run this script from the root of the project, use 'cd ..' to move up one directory")
            sys.exit(1)
    # end ............................................. RunTests ........................................... -> test_2 #

    def _3(self) -> None: # .......................................................................................... #
        raise NotImplementedError("test_3 is not yet implemented")
    # end ............................................. RunTests ........................................... -> test_3 #
# end ....................................................................................................... RunTests #
