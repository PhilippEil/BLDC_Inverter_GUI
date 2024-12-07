"""uartHelper.py
Tis file contains the UART helper calss. It handels all the work whit the MCU Comunication.


"""
__author__ = "Philipp Eilmann"
__version__ = "0.0.1"

import threading
import logging
import serial
import serial.tools.list_ports
import struct
import enum

logger = logging.getLogger(__name__)

class Command(enum.Enum):
    NONE = 0x00
    SET_PWM = 0x01
    SET_RPM = 0x02
    SET_COMMUTATION = 0x03
    ENABLE = 0x04
    CONTROL_MODE = 0x05
    P_VALUE = 0x06
    I_VALUE = 0x07
    D_VALUE = 0x08
    GET_STATE = 0x09

CommutationsType = {
    "Blockkomutirung 120 Unipolar": 0x10, 
    "Blockkomutirung 120 Bipolar": 0x11, 
    "Blockkomutirung 180 Unipolar":0x20, 
    "Blockkomutirung 180 Bipolar": 0x21, 
    "S-PWM": 0x30,
}

def crc8(data):
    crc = 0
    for byte in data:
        crc ^= byte
    return crc

class TextMessage:
    def __init__(self, data):
        self.text = data.strip()
    
    def __str__(self):
        return f"TextMessage: {self.text}"

class RX_UART_Message:
    _format = 'HhBhhh'
    _raw = b''
    rpm, voltage, PWM, currentA, currentB, currentC = 0, 0, 0, 0, 0, 0

    def __str__(self):
        return f"RPM: {self.rpm}, Voltage: {self.voltage:.2f}, PWM: {self.PWM}, Current A: {self.currentA:.2f}, Current B: {self.currentB:.2f}, Current C: {self.currentC:.2f}"
    
    def __len__(self) -> int:
        return struct.calcsize(self._format)
    
    def raw(self):
        return self._raw
    
    def decode(self, data):
        self._raw = data
        self.rpm, voltage, self.PWM, currentA, currentB, currentC = struct.unpack('HhBhhh', data[-12:])
        self.currentA = float(currentA / 1000)
        self.currentB = float(currentB / 1000)
        self.currentC = float(currentC / 1000)
        self.voltage = float(voltage / 1000)
        
class RX_UART_Message_Frame:
    _format = 'B13sBBB'
    _newMessage = False
    start_bit, crc, end_bit, EOL  = 0, 0, 0, 0
    message = RX_UART_Message()
  
    def __str__(self):
        return f"Start: {hex(self.start_bit)}, {self.message}, CRC: {hex(self.crc)}, End: {hex(self.end_bit)}, EOL: {hex(self.EOL)}"
    def __len__(self) -> int:
        return struct.calcsize(self._format)
    
    def isValide(self):
        crc = crc8(self.message.raw())
        return self.start_bit == 0x5B and self.end_bit == 0x5D and self.crc == crc
    
    def isAvailable(self):
        if self.isValide() and self._newMessage:
            self._newMessage = False
            return True
        return False
    
    def decode(self, data): 
        self.start_bit, message_data, self.crc, self.end_bit, self.EOL = struct.unpack(self._format, data)
        self.message.decode(message_data)
        self._newMessage = True

class TX_UART_Message:
    _format = 'BIIBBB'
    _start_bit = 0x3A
    _end_bit = 0x3B
    _crc = 0
    _EOL = 0x0A
    paload:int=0
    command:int=0
    
    def __str__(self):
        return f"command: {self.command}, paload: {self.paload}"
    
    def __len__(self) -> int:
        return struct.calcsize(self._format)
    
    def encode(self):
        if type(self.command) == Command:
            self.command = self.command.value
        massage = struct.pack('II', self.command, self.paload)
        self._crc = crc8(massage)
        return struct.pack(self._format, self._start_bit, self.command, self.paload, self._crc, self._end_bit, self._EOL)


class UartHelper:
    
    rxMessage = RX_UART_Message_Frame()
    
    def __init__(self) -> None:
        """Init the class
        """
        self.ser = serial.Serial()
        self.ser.baudrate = 115200
        self.ser.timeout = 1
        self.read_thread = None
        self.reading = False
        self.buffer = bytearray()
        self.message_stack = []
        
        logger.info("Init version")
    
    def cleanUp(self) -> None:
        self._stop_reading()
        logger.info("Clean up done")
        
    def connect(self, isinstance: str) -> bool:
        self.ser.port = isinstance
        self.ser.open()
        self._start_reading()
        logger.info(f"Connecting to: {isinstance}")
        return True
    
    def disconnect(self) -> bool:
        self._stop_reading()
        self.ser.close()
        logger.info("Disconnected")
        return True
    
    def listInstances(self) -> list:
        ports = serial.tools.list_ports.comports()
        ret = [port.device for port in ports]
        logger.info(f"The following instances are available: {ret}")
        return ret
    
    def send(self, message: TX_UART_Message) -> None:
        if not self.ser.is_open:
            logger.error("Serial port is not open")
            return
        self.ser.write(message.encode())
        logger.debug(f"Send: {message}")
        
    def getMassage(self):
        if len(self.message_stack) > 0:
            return self.message_stack.pop(0)
        return None
    
    def _start_reading(self):
        if not self.ser.is_open:
            logger.error("Serial port is not open")
            return
        
        self.reading = True
        self.read_thread = threading.Thread(target=self._read_from_port)
        self.read_thread.start()
    
    def _stop_reading(self):
        self.reading = False
        if self.read_thread is not None:
            self.read_thread.join()
    
    def _read_from_port(self):
        frame_size = len(self.rxMessage)
        self.ser.reset_input_buffer()
        while self.reading:
            if self.ser.in_waiting > 0:
                data = self.ser.read()
                self.buffer += data
                
                string = self.buffer.decode('utf-8', errors='ignore')
                index = string.find('OK')
                if index != -1:
                    self.message_stack.append(TextMessage(string[index:index+2]))
                    self.buffer = self.buffer[index+2:]
                    logger.debug("Recived OK")
                    
                index = string.find('ERROR')
                if index != -1:
                    self.message_stack.append(TextMessage(string[index:index+5]))
                    self.buffer = self.buffer[index+5:]
                    logger.debug("Recived ERROR")
                
                while len(self.buffer) >= frame_size:
                    start_index = -1
                    end_index = -1
                    
                    start_index = self.buffer.find(0x5B)
                    end_index = start_index + frame_size
                    
                    if start_index != -1 and end_index != -1 and end_index <= len(self.buffer):
                        frame_data = bytearray()
                        message = RX_UART_Message_Frame()
                        
                        for i in range(start_index, end_index):
                            frame_data.append(self.buffer[i])
                        try:
                            message.decode(frame_data)
                            logging.debug(f"Frame: {message}")
                        except struct.error as e:
                            logger.error(f"Error unpacking frame: {e}")
                            
                        if message.isValide():
                            self.buffer.clear()
                            self.message_stack.append(message.message)
                        else:
                            logging.debug("Invalid frame")
                            self.buffer = self.buffer[start_index+1:]
                    else:
                        break