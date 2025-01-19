

from moduls.guiHelper import GuiHelper, GuiAction
from moduls.uartHelper import UartHelper
from moduls.models.uartDefines import UART_Message, CommutationsType, MSG_Type, MSG_INDEX_PARAM, MSG_INDEX_STATUS
from moduls.models.dataClasses import SystemData, UARTSignals
import logging
import atexit
from copy import deepcopy
import time

logger = logging.getLogger(__name__)


class App:
    
    _SystemData = SystemData()
    
    def __init__(self):
        self.uart = UartHelper(self._SystemData.uartSignals)
        self.gui = GuiHelper(self.uart, self._SystemData, self.guiCallback)
        self.targetPwm = 0
        self.targetRpm = 0
        self.gui.startGui()
        print("Init done")
        
        
    def guiCallback(self, action, value):
        message = UART_Message()
        logger.debug(f"Action: {action}, Value: {value}")
        
        match action:
            case GuiAction.SET_PWM:
                message.type = MSG_Type.WRITE_REQUEST
                message.index = MSG_INDEX_PARAM.VALUE_PWM
                message.setPayloadUnsigned(value)
                self._SystemData.target_pwm = value
            case GuiAction.SET_COMMUTATION:
                message.type = MSG_Type.WRITE_REQUEST
                message.index = MSG_INDEX_PARAM.VALUE_COMMUTATION
                message.setPayloadUnsigned(CommutationsType[value])
                self._SystemData.commutation = CommutationsType[value]
            case GuiAction.SET_START:
                message.type = MSG_Type.WRITE_REQUEST
                message.index = MSG_INDEX_PARAM.VALUE_ENABLE
                message.setPayloadSigned(value)
                self._SystemData.enable = value
            case GuiAction.SET_CONTROL_MODE:
                message.type = MSG_Type.WRITE_REQUEST
                message.index = MSG_INDEX_PARAM.VALUE_CONTROLE_METHOD
                message.setPayloadUnsigned(value)
                self._SystemData.controle_method = value
            case GuiAction.SET_RPM:
                message.type = MSG_Type.WRITE_REQUEST
                message.index = MSG_INDEX_PARAM.VALUE_RPM
                message.setPayloadSigned(value)
                self._SystemData.target_rpm = value
            case GuiAction.SET_P_VALUE:
                message.type = MSG_Type.WRITE_REQUEST
                message.index = MSG_INDEX_PARAM.VALUE_PWM_P
                message.setPayloadSigned(int(value*1000))
                self._SystemData.pwm_p = int(value*1000)
            case GuiAction.SET_I_VALUE:
                message.type = MSG_Type.WRITE_REQUEST
                message.index = MSG_INDEX_PARAM.VALUE_PWM_I
                message.setPayloadSigned(int(value*1000))
                self._SystemData.pwm_i = int(value*1000)
            case GuiAction.SET_D_VALUE:
                message.type = MSG_Type.WRITE_REQUEST
                message.index = MSG_INDEX_PARAM.VALUE_PWM_D
                message.setPayloadSigned(int(value*1000))
                self._SystemData.pwm_d = int(value*1000)
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
        if message not in [None, False]:
            # logger.debug(f"Read the message: {message}")
            if message.type == MSG_Type.RESPONSE:
                for signal in self._SystemData.uartSignals:
                    if signal.index == message.index:
                        if signal.allow_negative:
                            signal.value = (message.getPayloadSigned()*signal.factor) + signal.offset
                        elif signal.isRaw:
                            signal.value = message.getPayloadUnsigned()
                        else:
                            signal.value = (message.getPayloadUnsigned()*signal.factor) + signal.offset
                        signal.lastReceived = time.time_ns()
                        break
                        
                self.gui.updateData(self._SystemData)
            
            if message.type == MSG_Type.STATUS_MESSAGE:
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
            
        
    def run(self):
        while self.gui.isGuiRunning():
            self.readUART()
            self.gui.renderWindow()