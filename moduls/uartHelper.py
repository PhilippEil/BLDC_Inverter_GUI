"""uartHelper.py
Tis file contains the UART helper calss. It handels all the work whit the MCU Comunication.


"""
__author__ = "Philipp Eilmann"
__version__ = "0.0.1"

import threading
import logging

logger = logging.getLogger(__name__)

class UartHelper:
    
    def __init__(self) -> None:
        """Init the class
        """
        logger.info(f"Init version:{__version__}")
        pass
    
    def cleanUp(self) -> None:
        logger.info("Clean up done")
        
    def connect(self,isinstance:str)-> bool:
        logger.info(F"Connecting to :{isinstance}")
        return True
    
    def disconnect(self)-> bool:
        logger.info(F"diconnected")
        return True
    
    def listInstances(self)->list:
        ret = ["Hsdjh","Dsd"]
        logger.info(f"The followig instances are avilabal :{ret}")
        return ret