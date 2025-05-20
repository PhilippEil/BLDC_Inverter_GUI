""" dataClasses.py

This module defines data classes for the UART signals and system data.
It includes the Signale class for individual signals and the UARTSignals class
for managing multiple signals.
It also defines the SystemData class for system-wide data.

@Author: Philipp Eilmann
@copyright: 2025 Philipp Eilmann
"""

__version__ = "0.0.2"

import dataclasses
from moduls.uartDefines import MSG_INDEX_PARAM
import time
import logging

logger = logging.getLogger(__name__)

@dataclasses.dataclass
class Signale:
    """
    Data class for the serial signals.

    Attributes:
    -----------
    name : str
        The name of the signal.
    value : int | float
        The value of the signal.
    unite : str
        The unit of the signal.
    index : MSG_INDEX_PARAM
        The index of the signal.
    factor : float, optional
        The factor to apply to the signal value (default is 1.0).
    offset : float, optional
        The offset to apply to the signal value (default is 0.0).
    allow_negative : bool, optional
        Whether the signal can have negative values (default is False).
    isRaw : bool, optional
        Whether the signal is raw (default is False).
    cycleTime : int, optional
        The cycle time for the signal in milliseconds (default is 1000).
    cyclic : bool, optional
        Whether the signal is cyclic (default is False).
    isPersistent : bool, optional
        Whether the signal is persistent (default is False)
    noRetransmit : bool, optional
        Whether to disable retransmission of the signal (default is False).     
    lastReceived : float, optional
        The timestamp of the last received signal (default is 0.0).
    lastTransmitted : float, optional
        The timestamp of the last transmitted signal (default is 0.0).
    valueWritten : bool, optional
        Whether the signal value has been written (default is False).
    newValue : int | float, optional
        The new value of the signal (default is 0).
    """
    name: str
    value: int | float
    unite: str
    index: MSG_INDEX_PARAM
    factor: float = 1.0
    offset: float = 0.0
    allow_negative: bool = False
    isRaw: bool = False
    cycleTime: int = 1000
    cyclic: bool = False
    isPersistent: bool = False
    noRetransmit: bool = False
    lastReceived: float = 0.0
    lastTransmitted: float = 0.0
    valueWritten: bool = False
    newValue: int | float = None
    
    def __eq__(self, value):
        """
        Check if the signal index is equal to the given value.
        """
        return self.index == value
    
    def __str__(self):
        """
        Return a string representation of the signal.
        """
        return f"{self.name}: {self.value} {self.unite}"
    
    def __iter__(self):
        """
        Return an iterator over the signal attributes.
        """
        return iter(dataclasses.asdict(self))
    
    def write(self, value: int | float):
        """
        Write a new value to the signal if it is different from the current value.

        Args:
            value (int | float): The new value to write.
        """
        if value != self.value:
            if self.isPersistent:
                self.value = value
            logger.debug(f"Write {self.name}: {self.value} {self.unite}")
            self.newValue = value
            self.valueWritten = True
            
    def update(self, value: int | float):
        """
        Update the signal value if it is different from the current value and not already written.

        Args:
            value (int | float): The new value to update.
        """
        if value != self.value and not self.valueWritten:
            if self.isRaw:
                self.value = value
                logger.debug(f"Update RAW {self.name}: {self.value} {self.unite}")
            else:
                self.value = (value * self.factor) + self.offset
                logger.debug(f"Update {self.name}: {self.value} {self.unite}")
        self.lastReceived = time.time_ns()
        
    def retransmit(self) -> None:
        """
        Retransmit the signal value if it was not yet overwritten.

        """
        logger.debug(f"Try to Retransmit {self.name}: {self.value = } {self.newValue = } {self.noRetransmit = }")
        if  not(self.newValue is None) and not self.noRetransmit:
            logger.debug(f"Retransmit {self.name}: {self.newValue} {self.unite}")
            self.valueWritten = True
        

    def getRaw(self):
        """
        Get the raw value of the signal.

        Returns:
            int | float: The raw value of the signal.
        """
        if not self.isRaw:
            return int((self.newValue - self.offset) / self.factor)
        return self.newValue

class UARTSignals:
    """
    Data class for the UART signals.

    Attributes:
    -----------
    bat_voltage : Signale
        The battery voltage signal.
    current_0 : Signale
        The current 0 signal.
    current_a : Signale
        The current A signal.
    current_b : Signale
        The current B signal.
    current_c : Signale
        The current C signal.
    temp_motor : Signale
        The motor temperature signal.
    temp_inverter : Signale
        The inverter temperature signal.
    rpm : Signale
        The RPM signal.
    pwm : Signale
        The PWM signal.
    controle_method : Signale
        The control method signal.
    commutation : Signale
        The commutation signal.
    swish_freq : Signale
        The swish frequency signal.
    enable : Signale
        The enable signal.
    pwm_p : Signale
        The PWM P signal.
    pwm_i : Signale
        The PWM I signal.
    pwm_d : Signale
        The PWM D signal.
    """
    def __init__(self):
        """
        Initialize the UART signals.
        """
        
        # Battery voltage signal
        self.bat_voltage: Signale = Signale(
            name="Bat Voltage",  # Name of the signal
            value=0.0,          # Default value
            unite="V",          # Unit of the signal
            index=MSG_INDEX_PARAM.VALUE_BAT_VOLTAGE,  # Index in UART communication
            factor=0.01,        # Scaling factor
            offset=0.0,         # Offset value
            allow_negative=False,  # Whether negative values are allowed
            isRaw=False,        # Whether the signal is raw
            cycleTime=30000,    # Cycle time in milliseconds
            cyclic=True,        # Whether the signal is cyclic
            isPersistent=False, # Whether the signal is persistent
            noRetransmit=True   # Whether retransmission is disabled
        )

        # Current signals
        self.current_0: Signale = Signale(
            name="Current 0",
            value=0.0,
            unite="A",
            index=MSG_INDEX_PARAM.VALUE_CURRENT_0,
            factor=0.001,
            offset=0.0,
            allow_negative=True,
            isRaw=False,
            cycleTime=1000,
            cyclic=True,
            isPersistent=False
        )
        self.current_a: Signale = Signale(
            name="Current A",
            value=0.0,
            unite="A",
            index=MSG_INDEX_PARAM.VALUE_CURRENT_A,
            factor=0.001,
            offset=0.0,
            allow_negative=True,
            isRaw=False,
            cycleTime=1000,
            cyclic=True,
            isPersistent=False
        )
        self.current_b: Signale = Signale(
            name="Current B",
            value=0.0,
            unite="A",
            index=MSG_INDEX_PARAM.VALUE_CURRENT_B,
            factor=0.001,
            offset=0.0,
            allow_negative=True,
            isRaw=False,
            cycleTime=1000,
            cyclic=True,
            isPersistent=False
        )
        self.current_c: Signale = Signale(
            name="Current C",
            value=0.0,
            unite="A",
            index=MSG_INDEX_PARAM.VALUE_CURRENT_C,
            factor=0.001,
            offset=0.0,
            allow_negative=True,
            isRaw=False,
            cycleTime=1000,
            cyclic=True,
            isPersistent=False
        )

        # Temperature signals
        self.temp_motor: Signale = Signale(
            name="Motor Temp",
            value=0.0,
            unite="°C",
            index=MSG_INDEX_PARAM.VALUE_TEMP_MOTOR,
            factor=0.1,
            offset=0,
            allow_negative=False,
            isRaw=False,
            cycleTime=30000,
            cyclic=True,
            isPersistent=False,
            noRetransmit=True
        )
        self.temp_inverter: Signale = Signale(
            name="Inverter Temp",
            value=0.0,
            unite="°C",
            index=MSG_INDEX_PARAM.VALUE_TEMP_INVERTER,
            factor=0.1,
            offset=0,
            allow_negative=False,
            isRaw=False,
            cycleTime=30000,
            cyclic=True,
            isPersistent=True
        )

        # RPM signal
        self.rpm: Signale = Signale(
            name="RPM",
            value=0,
            unite="1/min",
            index=MSG_INDEX_PARAM.VALUE_RPM,
            factor=1,
            offset=0,
            allow_negative=False,
            isRaw=False,
            cycleTime=500,
            cyclic=True,
            isPersistent=False
        )

        # PWM signal
        self.pwm: Signale = Signale(
            name="PWM",
            value=0,
            unite="%",
            index=MSG_INDEX_PARAM.VALUE_PWM,
            factor=1,
            offset=0,
            allow_negative=False,
            isRaw=False,
            cycleTime=500,
            cyclic=True,
            isPersistent=False
        )

        # Control method signal
        self.controle_method: Signale = Signale(
            name="Control Method",
            value=0,
            unite="",
            index=MSG_INDEX_PARAM.VALUE_CONTROLE_METHOD,
            factor=1,
            offset=0,
            allow_negative=False,
            isRaw=True,
            cycleTime=10000,
            cyclic=False,
            isPersistent=True
        )

        # Commutation signal
        self.commutation: Signale = Signale(
            name="Commutation",
            value=0,
            unite="",
            index=MSG_INDEX_PARAM.VALUE_COMMUTATION,
            factor=1,
            offset=0,
            allow_negative=False,
            isRaw=True,
            cycleTime=1000,
            cyclic=False,
            isPersistent=True
        )

        # Swish frequency signal
        self.swish_freq: Signale = Signale(
            name="Swish Freq",
            value=0,
            unite="Hz",
            index=MSG_INDEX_PARAM.VALUE_SWISH_FREQ,
            factor=1,
            offset=0,
            allow_negative=False,
            isRaw=True,
            cycleTime=1000,
            cyclic=False,
            isPersistent=True
        )

        # Enable signal
        self.enable: Signale = Signale(
            name="Enable",
            value=0,
            unite="",
            index=MSG_INDEX_PARAM.VALUE_ENABLE,
            factor=1,
            offset=0,
            allow_negative=False,
            isRaw=True,
            cycleTime=1000,
            cyclic=False,
            isPersistent=True,
            noRetransmit=True
        )

        # PID controller signals
        self.pwm_p: Signale = Signale(
            name="PWM P",
            value=0,
            unite="",
            index=MSG_INDEX_PARAM.VALUE_PWM_P,
            factor=0.001,
            offset=0,
            allow_negative=False,
            isRaw=False,
            cycleTime=1000,
            cyclic=False,
            isPersistent=True
        )
        self.pwm_i: Signale = Signale(
            name="PWM I",
            value=0,
            unite="",
            index=MSG_INDEX_PARAM.VALUE_PWM_I,
            factor=0.001,
            offset=0,
            allow_negative=False,
            isRaw=False,
            cycleTime=1000,
            cyclic=False,
            isPersistent=True
        )
        self.pwm_d: Signale = Signale(
            name="PWM D",
            value=0,
            unite="",
            index=MSG_INDEX_PARAM.VALUE_PWM_D,
            factor=0.001,
            offset=0,
            allow_negative=False,
            isRaw=False,
            cycleTime=1000,
            cyclic=False,
            isPersistent=True
        )

        # Remote PWM signal
        self.remote_pwm: Signale = Signale(
            name="Remote PWM",
            value=0,
            unite="%",
            index=MSG_INDEX_PARAM.VALUE_REMOTE_PWM,
            factor=1,
            offset=0,
            allow_negative=True,
            isRaw=False,
            cycleTime=1000,
            cyclic=True,
            isPersistent=True,
            noRetransmit=True
        )

    def __iter__(self):
        """
        Return an iterator over the UART signals.
        """
        for attr, value in self.__dict__.items():
            yield value

@dataclasses.dataclass
class SystemData:
    """
    Data class for the system data.

    Attributes:
    -----------
    uartSignals : UARTSignals
        An instance of UARTSignals containing UART signal definitions.
    target_current : float
        The target current value.
    target_rpm : int
        The target RPM value.
    target_pwm : int
        The target PWM value.
    updateSignalsAtConnect : bool
        Whether to update signals at connection (default is True).
    """
    uartSignals: UARTSignals = UARTSignals()
    target_current: float = 0.0
    target_rpm: int = 0
    target_pwm: int = 0
    updateSignalsAtConnect: bool = True