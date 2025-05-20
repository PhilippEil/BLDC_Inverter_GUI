""" uartDefines.py

Main module for defining UART message formats and handling CRC checks.
This module contains classes and enums for UART message types, indices,
and CRC checks. It also provides a class for cyclic sending of messages
at specified intervals.
    

@Author: Philipp Eilmann
@copyright: 2025 Philipp Eilmann
"""

__version__ = "0.0.2"
import struct
from enum import Enum
import dataclasses
import time
import logging

logger = logging.getLogger(__name__)

class MSG_Type(Enum):
    """Enum for the message type.
    """
    RESPONSE = 0x0
    STATUS_MESSAGE = 0x1
    WRITE_REQUEST = 0x2
    READ_REQUEST = 0x3
   
class MSG_INDEX_PARAM(Enum):
    """Enum for the message index.
    """
    VALUE_CURRENT_0 = 0x00
    VALUE_CURRENT_A = 0x01
    VALUE_CURRENT_B = 0x02
    VALUE_CURRENT_C = 0x03
    VALUE_BAT_VOLTAGE = 0x04
    VALUE_TEMP_MOTOR = 0x05
    VALUE_TEMP_INVERTER = 0x06
    VALUE_RPM = 0x07
    VALUE_PWM = 0x08
    VALUE_CONTROLE_METHOD = 0x09
    VALUE_COMMUTATION = 0x0A
    VALUE_SWISH_FREQ = 0x0B
    VALUE_ENABLE = 0x0C
    VALUE_PWM_P = 0x0D
    VALUE_PWM_I = 0x0E
    VALUE_PWM_D = 0x0F
    VALUE_REMOTE_PWM = 0x10
   
class MSG_INDEX_STATUS(Enum):
    """Enum for the message index.
    """
    STATUS_OK = 0x00
    STATUS_READY = 0x01
    STATUS_REMOTE_READY = 0x02
    STOP_EMERGENCY = 0x10
    STOP_OVER_TEMP = 0x11
    STOP_OVER_CURRENT = 0x12
    STOP_OVER_VOLTAGE = 0x13
    STOP_UNDER_VOLTAGE = 0x14
    STOP_SYSTEM_ERROR = 0x15
    STATUS_SYSTEM_ERROR = 0x3e
    STATUS_ERROR = 0x3f
   
CommutationsTypeValues = {
    "Blockkomutirung 120 Unipolar": 0x10, 
    "Blockkomutirung 120 Bipolar": 0x11, 
    "Blockkomutirung 180 Unipolar":0x20, 
    "Blockkomutirung 180 Bipolar": 0x21, 
    "S-PWM": 0x30,
}

SwishFrequencyValues = {
    "8 kHz": 0x09,
    "10 kHz": 0x10, 
    "20 kHz": 0x11, 
    "40 kHz": 0x20,
    "50 kHz": 0x21,
    "80 kHz": 0x30,
    "100 kHz": 0x31,
    "200 kHz": 0x40,
    "400 kHz": 0x41,
}

ControlMethodValues = {
    "Open Loop": 0x00,
    "RPM Control": 0x01,
    "Current Control": 0x02,
    "Remote Control": 0x03,
}
    
UpdateRates = {
    "15 ms": 15,
    "100 ms": 100,
    "250 ms": 250,
    "500 ms": 500,
    "1 s": 1000,
    "5 s": 5000,
    "10 s": 10000,
    "20 s": 20000,
    "30 s": 30000,
    "1 min": 60000,
}

class UART_Message:
    """
    Class for the UART message.

    Attributes:
        _format (str): The format string for struct packing/unpacking.
        _rawPayload (bytes): The raw payload of the message.
        raw (bytes): The raw data of the message.
        type (int): The type of the message.
        index (int): The index of the message.
        isValide (bool): Flag indicating if the message is valid.

    Methods:
        __str__(): Returns a string representation of the message.
        __len__(): Returns the length of the message.
        setPayloadUnsigned(value): Sets the payload as an unsigned integer.
        setPayloadSigned(value): Sets the payload as a signed integer.
        getPayloadUnsigned(): Gets the payload as an unsigned integer.
        getPayloadSigned(): Gets the payload as a signed integer.
        decode(data): Decodes the given data into the message format.
        encode(): Encodes the message into bytes.
    """
    _format = 'B2s'
    _rawPayload = b''
    raw = b''
    type, index = 0, 0
    isValide = True
    
    def __init__(self, type=None, index=None, payload=0):
        """
        Initialize the UART_Message class.

        Args:
            type (int, optional): The type of the message. Defaults to None.
            index (int, optional): The index of the message. Defaults to None.
            payload (int, optional): The payload of the message. Defaults to 0.
        """
        if type:
            self.type = type
        if index:
            self.index = index
        if payload:
            self.setPayloadSigned(payload)

    def __str__(self):
        if type(self.type) == MSG_Type and (type(self.index) == MSG_INDEX_PARAM or type(self.index) == MSG_INDEX_STATUS):
            return f"type: {self.type.name}, index: {self.index.name}, payload:{self.getPayloadUnsigned()}"
        else:
            return f"type: {hex(self.type)}, index: {hex(self.index)}, payload:{self.getPayloadSigned()}"

    def __len__(self) -> int:
        return struct.calcsize(self._format)

    def setPayloadUnsigned(self, value):
        """Sets the payload as an unsigned integer.

        Args:
            value (int): The unsigned integer value to set as the payload.
        """
        self._rawPayload = struct.pack('>H', value)

    def setPayloadSigned(self, value):
        """Sets the payload as a signed integer.

        Args:
            value (int): The signed integer value to set as the payload.
        """
        self._rawPayload = struct.pack('>h', value)

    def getPayloadUnsigned(self):
        """Gets the payload as an unsigned integer.

        Returns:
            int: The unsigned integer payload.
        """
        if len(self._rawPayload) == 0:
            return 0
        return struct.unpack('>H', self._rawPayload)[0]

    def getPayloadSigned(self):
        """Gets the payload as a signed integer.

        Returns:
            int: The signed integer payload.
        """
        if len(self._rawPayload) == 0:
            return 0
        return struct.unpack('>h', self._rawPayload)[0]

    def decode(self, data):
        """Decodes the given data into the message format.

        Args:
            data (bytes): The data to decode.
        """
        self.raw = data
        id, self._rawPayload = struct.unpack(self._format, data)
        self.type = MSG_Type(id >> 6)
        try:
            if self.type == MSG_Type.STATUS_MESSAGE:
                self.index = MSG_INDEX_STATUS(id & 0x3F)
            else:
                self.index = MSG_INDEX_PARAM(id & 0x3F)
        except ValueError:
            logger.error(f"Invalid message index: {hex(id & 0x3F)}")
            self.isValide = False

    def encode(self):
        """Encodes the message into bytes.

        Returns:
            bytes: The encoded message.
        """
        if type(self.type) == MSG_Type:
            self.type = self.type.value
        if type(self.index) == MSG_INDEX_PARAM:
            self.index = self.index.value
        if type(self.index) == MSG_INDEX_STATUS:
            self.index = self.index.value

        id = (self.type << 6) | (self.index & 0x3F)
        return struct.pack(self._format, id, self._rawPayload)


class UART_Message_Frame:
    """
    Class for the UART message frame.

    Attributes:
        _format (str): The format string for struct packing/unpacking.
        start_byte (int): The start byte of the frame.
        message_raw (bytes): The raw message data.
        crc (int): The CRC-8 checksum of the message.
        end_byte (int): The end byte of the frame.
        EOL (int): The end-of-line byte.
        _start_byte_Default (int): The default start byte.
        _end_byte_Default (int): The default end byte.
        _eol_Default (int): The default end-of-line byte.
        _newMessage (bool): Flag indicating if a new message is available.
        message (UART_Message): The UART message.

    Methods:
        __str__(): Returns a string representation of the message frame.
        __len__(): Returns the length of the message frame.
        _crc8(data): Calculates the CRC-8 checksum for the given data.
        decode(data): Decodes the given data into the message frame format.
        encode(): Encodes the message frame into bytes.
        isValide(): Checks if the message frame is valid by verifying the CRC.
        isAvailable(): Checks if a new valid message is available.
    """
    _format = 'B3sBBB'
    start_byte, message_raw, crc, end_byte, EOL = None, None, None, None, None
    _start_byte_Default = 0x3A
    _end_byte_Default = 0x3B
    _eol_Default = 0x0A
    _newMessage = False
    message = UART_Message()

    def __str__(self):
        return f"Start: {hex(self.start_byte)}, {self.message}, CRC: {hex(self.crc)}, End: {hex(self.end_byte)}, EOL: {hex(self.EOL)}"

    def __len__(self) -> int:
        return struct.calcsize(self._format)

    def _crc8(self, data) -> int:
        """Calculates the CRC-8 checksum for the given data.

        Args:
            data (bytes): The data to calculate the checksum for.

        Returns:
            int: The CRC-8 checksum.
        """
        crc = 0
        for byte in data:
            crc ^= byte
        return crc

    def decode(self, data):
        """Decodes the given data into the message frame format.

        Args:
            data (bytes): The data to decode.
        """
        self.start_byte, self.message_raw, self.crc, self.end_byte, self.EOL = struct.unpack(self._format, data)
        self.message.decode(self.message_raw)
        self._newMessage = True

    def encode(self):
        """Encodes the message frame into bytes.

        Returns:
            bytes: The encoded message frame.
        """
        if self.start_byte is None:
            self.start_byte = self._start_byte_Default
        if self.end_byte is None:
            self.end_byte = self._end_byte_Default
        if self.EOL is None:
            self.EOL = self._eol_Default
        if self.message_raw is None:
            self.message_raw = self.message.encode()
        self.crc = self._crc8(self.message_raw)
        return struct.pack(self._format, self.start_byte, self.message_raw, self.crc, self.end_byte, self.EOL)

    def isValide(self):
        """Checks if the message frame is valid by verifying the CRC.

        Returns:
            bool: True if the message frame is valid, False otherwise.
        """
        crc = self._crc8(self.message_raw)
        return self.start_byte == self._start_byte_Default and self.end_byte == self._end_byte_Default and self.crc == crc and self.message.isValide

    def isAvailable(self):
        """Checks if a new valid message is available.

        Returns:
            bool: True if a new valid message is available, False otherwise.
        """
        if self.isValide() and self._newMessage:
            self._newMessage = False
            return True
        return False
    
@dataclasses.dataclass
class CyclicSend:
    """
    The CyclicSend class represents a message that is sent at regular intervals.

    Attributes:
        message (UART_Message): The message to be sent.
        interval (int): The interval in milliseconds at which the message should be sent.
        lastSend (int): The timestamp of the last time the message was sent (default is 0).

    Methods:
        __str__(): Returns a formatted string containing the message, interval, and last send timestamp.
        isTime(): Checks if the interval has passed since the last time the message was sent.
    """
    message: UART_Message
    interval: int  
    lastSend: int = 0
    
    def __str__(self):
        return f"Message: {self.message}, Interval: {self.interval}, LastSend: {self.lastSend}"
    
    def isTime(self):
        """Checks if the interval has passed since the last time the message was sent.

        Returns:
            bool: True if the interval has passed, False otherwise.
        """
        if (time.time_ns() - self.lastSend) >= (self.interval * 1000000):
            self.lastSend = time.time_ns()
            return True
        return False