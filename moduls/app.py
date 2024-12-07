

from moduls.guiHelper import GuiHelper, GuiAction
from moduls.uartHelper import UartHelper, TX_UART_Message, TextMessage, RX_UART_Message, Command, CommutationsType
import logging
import atexit

logger = logging.getLogger(__name__)


class App:
    
    def __init__(self):
        self.uart = UartHelper()
        self.gui = GuiHelper(self.uart, self.guiCallback)
        self.targetPwm = 0
        self.targetRpm = 0
        self.gui.startGui()
        
    def guiCallback(self, action, value):
        message = TX_UART_Message()
        logger.debug(f"Action: {action}, Value: {value}")
        
        match action:
            case GuiAction.SET_PWM:
                message.command = Command.SET_PWM
                message.paload = value
                self.targetPwm = value
            case GuiAction.SET_COMMUTATION:
                message.command = Command.SET_COMMUTATION
                message.paload = CommutationsType[value]
            case GuiAction.SET_START:
                message.command = Command.ENABLE
                message.paload = value
            case GuiAction.SET_CONTROL_MODE:
                message.command = Command.CONTROL_MODE
                message.paload = value
            case GuiAction.SET_RPM:
                message.command = Command.SET_RPM
                message.paload = value
                self.targetRpm = value
            case GuiAction.SET_P_VALUE:
                message.command = Command.P_VALUE
                message.paload = int(value*1000)
            case GuiAction.SET_I_VALUE:
                message.command = Command.I_VALUE
                message.paload = int(value*1000)
            case GuiAction.SET_D_VALUE:
                message.command = Command.D_VALUE
                message.paload = int(value*1000)
            case _:
                logger.error(f"Unknown action: {action}")
                return
        self.gui.writeLog(message, Tx=True)
        self.uart.send(message)
        
        
    def cleanUp(self):
        self.uart.cleanUp()
        self.gui.cleanUp()

    def readUART(self):
        message = self.uart.getMassage()
        if type(message) == RX_UART_Message:
        
            global targetPwm, targetRpm
            
            self.gui.abentToPlot(
                valueA=message.currentA, 
                valueB=message.currentB, 
                valueC=message.currentC,
                rpmActual=message.rpm, 
                rpmTarget=self.targetRpm,
                pwmActual=message.PWM, 
                pwmTarget=self.targetPwm
                )
            self.gui.writeLog(message, Rx=True)
            
        elif type(message) == TextMessage:
            self.gui.writeLog(message.text, Rx=True)
        
    def run(self):
        while self.gui.isGuiRunning():
            self.readUART()
            self.gui.renderWindow()