""" uartHelper.py

This module provides a helper class for UART communication with the MCU.
It includes methods for connecting to a serial port, sending and receiving messages,
and managing cyclic sending of messages.
It also includes methods for updating signal values by sending read requests.

@Author: Philipp Eilmann
@copyright: 2025 Philipp Eilmann
"""

__version__ = "0.0.2"

import threading
import logging
import serial
import serial.tools.list_ports
import time
from copy import deepcopy
from moduls.uartDefines import UART_Message, UART_Message_Frame, MSG_Type, CyclicSend
from moduls.dataClasses import Signale, UARTSignals

logger = logging.getLogger(__name__)

class UartHelper:
    """
    UartHelper class to handle UART communication with the MCU.

    This class provides methods to:
    - Connect and disconnect from a serial port.
    - Send and receive UART messages.
    - Manage cyclic sending of messages.
    - Update signal values by sending read requests.

    Attributes:
    -----------
    rxMessage : UART_Message_Frame
        A frame to hold the received UART message.
    _cyclicSend : list
        A list to hold cyclic send messages.
    _cyclicSendLock : threading.Lock
        A lock to manage access to the cyclic send list.
    _cyclicSendThread : threading.Thread
        A thread to handle cyclic sending of messages.
    _read_thread : threading.Thread
        A thread to handle reading from the serial port.
    ser : serial.Serial
        The serial port object.
    read_thread : threading.Thread
        The thread used for reading from the serial port.
    reading : bool
        A flag to indicate if reading from the serial port is active.
    buffer : bytearray
        A buffer to hold incoming data from the serial port.
    message_stack : list
        A stack to hold received messages.
    _uartSignals : UARTSignals
        An instance of UARTSignals containing signal definitions.
    isSending : bool
        A flag to indicate if cyclic sending is active.

    Methods:
    --------
    cleanUp() -> None:
        Clean up resources by stopping reading and cyclic send threads.
    
    connect(port: str) -> bool:
        Connect to the specified serial port and start reading and cyclic send threads.
    
    disconnect() -> bool:
        Disconnect from the serial port and stop reading and cyclic send threads.
    
    listInstances() -> list:
        List available serial ports.
    
    send(message: UART_Message) -> None:
        Send a UART message.
    
    getMessage():
        Get the next message from the message stack.
    
    addCyclicSend(message: UART_Message, interval: int) -> None:
        Add a message to be sent cyclically.
    
    _start_reading() -> None:
        Start the reading thread.
    
    _stop_reading() -> None:
        Stop the reading thread.
    
    _start_cyclic_send() -> None:
        Start the cyclic send thread.
    
    _stop_cyclic_send() -> None:
        Stop the cyclic send thread.
    
    _updateSignals() -> None:
        Update the signals by sending read requests.
    
    _read_from_port() -> None:
        Read data from the serial port.
    
    _send_cyclic() -> None:
        Send cyclic messages.
    """

    rxMessage = UART_Message_Frame()
    _cyclicSend = []
    _cyclicSendLock = threading.Lock()
    _cyclicSendThread = threading.Thread()
    _read_thread = threading.Thread()
    
    def __init__(self, uartSignals: UARTSignals) -> None:
        """
        Initialize the UartHelper class.

        Args:
            uartSignals (UARTSignals): An instance of UARTSignals containing signal definitions.
        """
        self.ser = serial.Serial(baudrate=115200, timeout=1)
        self.read_thread = None
        self.reading = False
        self.message_stack = []
        self._uartSignals = uartSignals
        self.isSending = False
        logger.info(f"Init version: {__version__}")
    
    def cleanUp(self) -> None:
        """
        Clean up resources by stopping reading and cyclic send threads.
        """
        self._stop_reading()
        self._stop_cyclic_send()
        logger.info("Clean up done")
        
    def connect(self, port: str, updateSignals:bool=False) -> bool:
        """
        Connect to the specified serial port and start reading and cyclic send threads.

        Args:
            port (str): The serial port to connect to.
            updateSignals (bool): Flag to indicate if signals should be updated after connection.

        Returns:
            bool: True if connection is successful, False otherwise.
        """
        if self.ser.is_open:
            logger.error("Serial port is already open")
            return False
        self.ser.port = port
        self.ser.open()
        if not self.ser.is_open:
            logger.error(f"Failed to open serial port: {port}")
            return False
        self.ser.reset_input_buffer()
        self.ser.reset_output_buffer()
        self._start_reading()
        self._start_cyclic_send()
        logger.info(f"Connecting to: {port}")
        if updateSignals:
            self._updateSignals()
        else:
            logger.info("No signal update requested")
        self._updateSignals()
        return True
    
    def disconnect(self) -> bool:
        """
        Disconnect from the serial port.

        Returns:
            bool: True if disconnection is successful, False otherwise.
        """
        self._stop_reading()
        self._stop_cyclic_send()
        if not self.ser.is_open:
            logger.error("Serial port is not open")
            self.ser.close()
        logger.info("Disconnected")
        return True
    
    def listInstances(self) -> list:
        """
        List available serial ports.

        Returns:
            list: A list of available serial ports.
        """
        ports = serial.tools.list_ports.comports()
        ret = [port.device for port in ports]
        logger.info(f"The following instances are available: {ret}")
        return ret
    
    def send(self, message: UART_Message) -> None:
        """
        Send a UART message.

        Args:
            message (UART_Message): The UART message to send.
        """
        if not self.ser.is_open:
            logger.error("Serial port is not open")
            return
        buf = UART_Message_Frame()
        buf.message = message
        self.ser.write(buf.encode())
        logger.debug(f"Send: {buf}")
        
    def getMessage(self):
        """
        Get the next message from the message stack.

        Returns:
            UART_Message: The next message from the message stack, or None if the stack is empty.
        """
        if self.message_stack:
            return self.message_stack.pop(0)
        return None
    
    def addCyclicSend(self, message: UART_Message, interval: int) -> None:
        """
        Add a message to be sent cyclically.

        Args:
            message (UART_Message): The UART message to send cyclically.
            interval (int): The interval in milliseconds between each send.
        """
        self._stop_cyclic_send()
        cyclic = CyclicSend(deepcopy(message), interval)
        self._cyclicSend.append(cyclic)
        self._start_cyclic_send()
        logger.debug(f"Added cyclic send: {cyclic}")
    
    def _start_reading(self) -> None:
        """
        Start the reading thread.
        """
        if not self.ser.is_open:
            logger.error("Serial port is not open")
            return
        self.reading = True
        self._read_thread = threading.Thread(target=self._read_from_port)
        self._read_thread.start()
    
    def _stop_reading(self) -> None:
        """
        Stop the reading thread.
        """
        self.reading = False
        if self._read_thread.is_alive():
            self._read_thread.join()
    
    def _start_cyclic_send(self) -> None:
        """
        Start the cyclic send thread.
        """
        if not self.ser.is_open:
            logger.error("Serial port is not open")
            return
        self.isSending = True
        self._cyclicSendThread = threading.Thread(target=self._send_cyclic)
        self._cyclicSendThread.start()
        
    def _stop_cyclic_send(self) -> None:
        """
        Stop the cyclic send thread.
        """
        self.isSending = False
        if self._cyclicSendThread.is_alive():
            self._cyclicSendThread.join()
            
    def _updateSignals(self) -> None:
        """
        Update the signals by sending read requests.
        """
        if not self.ser.is_open:
            logger.error("Serial port is not open")
            return
        for signal in self._uartSignals:
            message = UART_Message(type=MSG_Type.READ_REQUEST, index=signal.index)
            signal.lastTransmitted = time.time_ns()
            self.send(message)
            time.sleep(0.01)
    
    def _read_from_port(self) -> None:
        """
        Read data from the serial port.
        """
        frame_size = len(self.rxMessage)
        self.ser.reset_input_buffer()
        append = self.message_stack.append
        buffer = bytearray()
        message = UART_Message_Frame()
        while self.reading:
            if self.ser.in_waiting > 0:
                data = self.ser.read(self.ser.in_waiting)
                buffer += data

                while len(buffer) >= frame_size:
                    start_index = buffer.find(0x3A)
                    if start_index == -1:
                        break

                    end_index = start_index + frame_size
                    if end_index > len(buffer):
                        break

                    frame_data = buffer[start_index:end_index]
                    try:
                        message.decode(frame_data)
                        logging.debug(f"Frame: {message}")
                    except Exception as e:
                        logger.error(f"Error unpacking frame: {e}")

                    if message.isValide():
                        append(deepcopy(message.message))
                        buffer = buffer[end_index:]
                    else:
                        logging.debug("Invalid frame")
                        buffer = buffer[start_index+1:]
    
    def _send_cyclic(self) -> None:
        """
        Send cyclic messages.
        """
        send = self.send
        time_ns = time.time_ns
        while self.isSending:
            current_time = time_ns()
            for signal in self._uartSignals:
                if signal.valueWritten:
                    msg = UART_Message(type=MSG_Type.WRITE_REQUEST, index=signal.index)
                    msg.setPayloadSigned(signal.getRaw())
                    signal.valueWritten = False
                    signal.lastTransmitted = current_time
                    send(msg)
                elif signal.cyclic and signal.lastTransmitted + (signal.cycleTime * 1000000) < current_time:
                    msg = UART_Message(type=MSG_Type.READ_REQUEST, index=signal.index)
                    signal.lastTransmitted = current_time
                    send(msg)
            time.sleep(0.002)