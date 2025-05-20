""" app.py

Main application class to handle the GUI and UART communication.
This class is responsible for initializing the GUI and UART components,
reading messages from the UART, and updating the GUI with the received data.

@Author: Philipp Eilmann
@copyright: 2025 Philipp Eilmann
"""

__version__ = "0.0.2"

from moduls.guiHelper import GuiHelper
from moduls.uartHelper import UartHelper
from moduls.uartDefines import MSG_Type, MSG_INDEX_STATUS
from moduls.dataClasses import SystemData
import logging


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
                        self.gui.writeLog("Transmitting settings to ESC")
                        for signal in self._SystemData.uartSignals:
                            signal.retransmit()
                            
                    case MSG_INDEX_STATUS.STATUS_REMOTE_READY:
                        self.gui.writeLog("MCU Status Remote Ready", Rx=True)
                    
                    case MSG_INDEX_STATUS.STOP_EMERGENCY:
                        self.gui.writeLog("MCU Status Emergency Stop", Rx=True)
                    
                    case MSG_INDEX_STATUS.STATUS_SYSTEM_ERROR:
                        self.gui.writeLog(f"MCU Status System Error: {message.getPayloadSigned()}", Rx=True)
                    
                    case MSG_INDEX_STATUS.STATUS_ERROR:
                        self.gui.writeLog(f"MCU Status Error: {message.getPayloadSigned()}", Rx=True)
                    
                    case _:
                        self.gui.writeLog(f"MCU Status Unknown: {message.getPayloadSigned()}", Rx=True)
                        logger.error(f"Unknown message index: {message.index}")
                        return
            if newData:
                # todo: remove this function and add a separate thread for the GUI
                self.gui.updateData(self._SystemData)
            message = self.uart.getMessage()
            
        
    def run(self):
        self.gui.writeLog("Starting GUI")
        while self.gui.isGuiRunning():
            self.readUART()
            self.gui.renderWindow()