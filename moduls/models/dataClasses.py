""" dataClasses.py
Data classes for the application

@Author: Philipp Eilmann
@Version: 0.0.1
"""

import dataclasses
from moduls.models.uartDefines import MSG_INDEX_PARAM
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
        Whether the signal is persistent (default is False).
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
    lastReceived: float = 0.0
    lastTransmitted: float = 0.0
    valueWritten: bool = False
    newValue: int | float = 0
    
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
        self.bat_voltage: Signale = Signale("Bat Voltage", 0.0, "V", MSG_INDEX_PARAM.VALUE_BAT_VOLTAGE, 0.01, 0.0, False, False, 30000, True, False)
        self.current_0: Signale = Signale("Current 0", 0.0, "A", MSG_INDEX_PARAM.VALUE_CURRENT_0, 0.001, 0.0, True, False, 1000, True, False)
        self.current_a: Signale = Signale("Current A", 0.0, "A", MSG_INDEX_PARAM.VALUE_CURRENT_A, 0.001, 0.0, True, False, 1000, True, False)
        self.current_b: Signale = Signale("Current B", 0.0, "A", MSG_INDEX_PARAM.VALUE_CURRENT_B, 0.001, 0.0, True, False, 1000, True, False)
        self.current_c: Signale = Signale("Current C", 0.0, "A", MSG_INDEX_PARAM.VALUE_CURRENT_C, 0.001, 0.0, True, False, 1000, True, False)
        self.temp_motor: Signale = Signale("Motor Temp", 0.0, "°C", MSG_INDEX_PARAM.VALUE_TEMP_MOTOR, 0.1, 0, False, False, 30000, True, False)
        self.temp_inverter: Signale = Signale("Inverter Temp", 0.0, "°C", MSG_INDEX_PARAM.VALUE_TEMP_INVERTER, 0.1, 0, False, False, 30000, True)
        self.rpm: Signale = Signale("RPM", 0, "1/min", MSG_INDEX_PARAM.VALUE_RPM, 1, 0, True, False, 1000, True, False)
        self.pwm: Signale = Signale("PWM", 0, "%", MSG_INDEX_PARAM.VALUE_PWM, 1, 0, False, False, 1000, True, False)
        self.controle_method: Signale = Signale("Control Method", 0, "", MSG_INDEX_PARAM.VALUE_CONTROLE_METHOD, 1, 0, False, True, 10000, False, True)
        self.commutation: Signale = Signale("Commutation", 0, "", MSG_INDEX_PARAM.VALUE_COMMUTATION, 1, 0, False, True, 1000, False, True)
        self.swish_freq: Signale = Signale("Swish Freq", 0, "Hz", MSG_INDEX_PARAM.VALUE_SWISH_FREQ, 1, 0, False, True, 1000, False, True)
        self.enable: Signale = Signale("Enable", 0, "", MSG_INDEX_PARAM.VALUE_ENABLE, 1, 0, False, True, 1000, False, True)
        self.pwm_p: Signale = Signale("PWM P", 0, "", MSG_INDEX_PARAM.VALUE_PWM_P, 1, 0, False, False, 1000, False, True)
        self.pwm_i: Signale = Signale("PWM I", 0, "", MSG_INDEX_PARAM.VALUE_PWM_I, 1, 0, False, False, 1000, False, True)
        self.pwm_d: Signale = Signale("PWM D", 0, "", MSG_INDEX_PARAM.VALUE_PWM_D, 1, 0, False, False, 1000, False, True)

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