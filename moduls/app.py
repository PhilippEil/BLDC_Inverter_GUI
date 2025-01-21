""" app.py
Main application class to handle the GUI and UART communication

@Author: Philipp Eilmann
@Version: 0.0.1
"""

from moduls.guiHelper import GuiHelper
from moduls.uartHelper import UartHelper
from moduls.models.uartDefines import MSG_Type, MSG_INDEX_STATUS
from moduls.models.dataClasses import SystemData
import logging
from moduls.timing import time_it


logger = logging.getLogger(__name__)

class App:
    """
    Main application class to handle the GUI and UART communication.

    Attributes:
    -----------
    _SystemData : SystemData
        An instance of SystemData containing system-wide data.
    uart : UartHelper
        An instance of UartHelper to handle UART communication.
    gui : GuiHelper
        An instance of GuiHelper to handle the GUI.

    Methods:
    --------
    __init__() -> None:
        Initialize the App class.
    
    cleanUp() -> None:
        Clean up resources by stopping UART and GUI components.
    
    readUART() -> None:
        Read and process UART messages.
    
    run() -> None:
        Run the main application loop.
    """
    
    _SystemData = SystemData()
    
    def __init__(self):
        """
        Initialize the App class.
        """
        self.uart = UartHelper(self._SystemData.uartSignals)
        self.gui = GuiHelper(self.uart, self._SystemData)
        self.gui.startGui()
    
    def cleanUp(self):
        """
        Clean up resources by stopping UART and GUI components.
        """
        self.uart.cleanUp()
        self.gui.cleanUp()

    def readUART(self):
        """
        Read and process UART messages.
        """
        message = self.uart.getMessage()
        newData = False
        signal_dict = {signal.index: signal for signal in self._SystemData.uartSignals}
        while message is not None:
            logger.debug(f"Read the message: {message}")
            if message.type == MSG_Type.RESPONSE:
                # Process response messages
                signal = signal_dict.get(message.index)
                if signal:
                    newData = True
                    if signal.allow_negative:
                        signal.update(message.getPayloadSigned())
                    else:
                        signal.update(message.getPayloadUnsigned())
            
            if message.type == MSG_Type.STATUS_MESSAGE:
                # Process status messages
                match message.index:
                    case MSG_INDEX_STATUS.STATUS_OK:
                        self.gui.writeLog("MCU Status OK", Rx=True)
                    case MSG_INDEX_STATUS.STATUS_READY:
                        self.gui.writeLog("MCU Status Ready", Rx=True)
                    case MSG_INDEX_STATUS.STATUS_SYSTEM_ERROR:
                        self.gui.writeLog(f"MCU Status System Error: {message.getPayloadSigned()}", Rx=True)
                    case MSG_INDEX_STATUS.STATUS_ERROR:
                        self.gui.writeLog(f"MCU Status Error: {message.getPayloadSigned()}", Rx=True)
                    case _:
                        logger.error(f"Unknown message index: {message.index}")
                        return
            if newData:
                # todo: remove this function and add a separate thread for the GUI
                self.gui.updateData(self._SystemData)
            message = self.uart.getMessage()
            
        
    def run(self):
        while self.gui.isGuiRunning():
            self.readUART()
            self.gui.renderWindow()