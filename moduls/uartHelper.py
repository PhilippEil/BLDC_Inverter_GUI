""" uartHelper.py
Tis file contains the UART helper calss. It handels all the work whit the MCU Comunication.

@Author: Philipp Eilmann
@Version: 0.0.3
"""

import threading
import logging
import serial
import serial.tools.list_ports
import time
from copy import deepcopy
from moduls.models.uartDefines import *
from moduls.models.dataClasses import Signale, UARTSignals

logger = logging.getLogger(__name__)

class UartHelper:
    
    rxMessage = UART_Message_Frame()
    _cyclicSend = []
    _cyclicSendLock = threading.Lock()
    _cyclicSendThread = threading.Thread()
    _read_thread = threading.Thread()
    
    
    def __init__(self, uartSignals:UARTSignals ) -> None:
        """Init the class
        """
        self.ser = serial.Serial()
        self.ser.baudrate = 115200
        self.ser.timeout = 1
        self.read_thread = None
        self.reading = False
        self.buffer = bytearray()
        self.message_stack = []
        self._uartSignals = uartSignals
        logger.info("Init version")
    
    def cleanUp(self) -> None:
        self._stop_reading()
        self._stop_cyclic_send()
        logger.info("Clean up done")
        
    def connect(self, isinstance: str) -> bool:
        self.ser.port = isinstance
        self.ser.open()
        self._start_reading()
        self._start_cyclic_send()
        logger.info(f"Connecting to: {isinstance}")
        return True
    
    def disconnect(self) -> bool:
        self._stop_reading()
        self._stop_cyclic_send()
        self.ser.close()
        logger.info("Disconnected")
        return True
    
    def listInstances(self) -> list:
        ports = serial.tools.list_ports.comports()
        ret = [port.device for port in ports]
        logger.info(f"The following instances are available: {ret}")
        return ret
    
    def send(self, message: UART_Message) -> None:
        if not self.ser.is_open:
            logger.error("Serial port is not open")
            return
        buf = UART_Message_Frame()
        buf.message = message
        self.ser.write(buf.encode())
        logger.debug(f"Send: {buf}")
        
    def getMassage(self):
        if len(self.message_stack) > 0:
            return self.message_stack.pop(0)
        return None
    
    def addCyclicSend(self, message: UART_Message, interval: int) -> None:
        self._stop_cyclic_send()
        cyclic = CyclicSend(deepcopy(message), interval)
        self._cyclicSend.append(cyclic)
        self._start_cyclic_send()
        logger.debug(f"Added cyclic send: {cyclic}")
    
    def _start_reading(self):
        if not self.ser.is_open:
            logger.error("Serial port is not open")
            return
        self.reading = True
        self._read_thread = threading.Thread(target=self._read_from_port)
        self._read_thread.start()
    
    def _stop_reading(self):
        self.reading = False
        if self._read_thread.is_alive():
            self._read_thread.join()
    
    def _start_cyclic_send(self):
        if not self.ser.is_open:
            logger.error("Serial port is not open")
            return
        # if len(self._cyclicSend) == 0:
        #     logger.info("No cyclic send messages available")
        #     return
        self.isSending = True
        self._cyclicSendThread = threading.Thread(target=self._send_cyclic)
        self._cyclicSendThread.start()
        
    def _stop_cyclic_send(self):
        self.isSending = False
        if self._cyclicSendThread.is_alive():
            self._cyclicSendThread.join()
    
    def _read_from_port(self):
        frame_size = len(self.rxMessage)
        self.ser.reset_input_buffer()
        while self.reading:
            if self.ser.in_waiting > 0:
                data = self.ser.read()
                self.buffer += data
                
                while len(self.buffer) >= frame_size:
                    start_index = -1
                    end_index = -1
                    
                    start_index = self.buffer.find(0x3A)
                    end_index = start_index + frame_size
                    
                    if start_index != -1 and end_index != -1 and end_index <= len(self.buffer):
                        frame_data = self.buffer[start_index:end_index]
                        message = UART_Message_Frame()
                        try:
                            message.decode(frame_data)
                            logging.debug(f"Frame: {message}")
                        except struct.error as e:
                            logger.error(f"Error unpacking frame: {e}")
                            
                        if message.isValide():
                            self.buffer.clear()
                            self.message_stack.append(deepcopy(message.message))
                        else:
                            logging.debug("Invalid frame")
                            self.buffer = self.buffer[start_index+1:]
                    else:
                        break
    
    def _send_cyclic(self):
        while self.isSending:
            for signal in self._uartSignals:
                if signal.cyclic and signal.lastReceived + (signal.cycleTime * 1000000)< time.time_ns():
                    message = UART_Message()
                    message.type = MSG_Type.READ_REQUEST
                    message.index = signal.index
                    #signal.lastReceived = time.time_ns()
                    self.send(message)
            time.sleep(0.001)