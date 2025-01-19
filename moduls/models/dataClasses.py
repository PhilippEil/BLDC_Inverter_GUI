""" dataClasses.py
Data classes for the application

@Author: Philipp Eilmann
@Version: 0.0.1
"""

import dataclasses
from moduls.models.uartDefines import MSG_INDEX_PARAM

@dataclasses.dataclass
class Signale:
    """Data class for the serial signals.
    """
    name: str
    value: int|float|str
    unite: str
    index: MSG_INDEX_PARAM
    factor: float = 1.0
    offset: float = 0.0
    allow_negative: bool = False
    isRaw: bool = False
    cycleTime: int = 1000
    cyclic: bool = False
    lastReceived = 0.0
    
    
    def __eq__(self, value):
        return self.index == value
    
    def __str__(self):
        return f"{self.name}: {self.value} {self.unite}"
    
    def __iter__(self):
        return iter(dataclasses.asdict(self))
    
    
    
class UARTSignals:
    """Data class for the UART signals.
    """
    def __init__(self):
        self.bat_voltage:Signale = Signale("Bat Voltage", 0.0, "V",MSG_INDEX_PARAM.VALUE_BAT_VOLTAGE, 0.01, 0.0, False, False, 30000, True)
        self.current_0:Signale = Signale("Current 0", 0.0, "A", MSG_INDEX_PARAM.VALUE_CURRENT_0, 0.001, 0.0, True, False, 1000, True)
        self.current_a:Signale = Signale("Current A", 0.0, "A", MSG_INDEX_PARAM.VALUE_CURRENT_A, 0.001, 0.0, True, False, 1000, True)
        self.current_b:Signale = Signale("Current B", 0.0, "A", MSG_INDEX_PARAM.VALUE_CURRENT_B, 0.001, 0.0, True, False, 1000, True)
        self.current_c:Signale = Signale("Current C", 0.0, "A", MSG_INDEX_PARAM.VALUE_CURRENT_C, 0.001, 0.0, True, False, 1000, True)
        self.temp_motor:Signale = Signale("Motor Temp", 0.0, "°C", MSG_INDEX_PARAM.VALUE_TEMP_MOTOR, 0.1, 0, False, False, 30000, True)
        self.temp_inverter:Signale = Signale("Inverter Temp", 0.0, "°C", MSG_INDEX_PARAM.VALUE_TEMP_INVERTER, 0.1, 0, False, False, 30000, True)
        self.rpm:Signale = Signale("RPM", 0, "1/min", MSG_INDEX_PARAM.VALUE_RPM, 1, 0, True, False, 1000, True)
        self.pwm:Signale = Signale("PWM", 0, "%", MSG_INDEX_PARAM.VALUE_PWM, 1, 0, False, False, 1000, True)
        self.controle_method:Signale = Signale("Control Method", 0, "", MSG_INDEX_PARAM.VALUE_CONTROLE_METHOD, 1, 0, False, True, 1000)
        self.commutation:Signale = Signale("Commutation", 0, "", MSG_INDEX_PARAM.VALUE_COMMUTATION, 1, 0, False, True, 1000)
        self.swish_freq:Signale = Signale("Swish Freq", 0, "Hz", MSG_INDEX_PARAM.VALUE_SWISH_FREQ, 1, 0, False, True, 1000)
        self.enable:Signale = Signale("Enable", 0, "", MSG_INDEX_PARAM.VALUE_ENABLE, 1, 0, False, True, 1000)
        self.pwm_p:Signale = Signale("PWM P", 0, "", MSG_INDEX_PARAM.VALUE_PWM_P, 1, 0, False, False, 1000)
        self.pwm_i:Signale = Signale("PWM I", 0, "", MSG_INDEX_PARAM.VALUE_PWM_I, 1, 0, False, False, 1000)
        self.pwm_d:Signale = Signale("PWM D", 0, "", MSG_INDEX_PARAM.VALUE_PWM_D, 1, 0, False, False, 1000)

    def __iter__(self):
        for attr, value in self.__dict__.items():
            yield value
       
    
@dataclasses.dataclass
class SystemData:
    """Data class for the system data.
    """
    uartSignals: UARTSignals = UARTSignals()
    bat_voltage: float = 0.0
    current_0: float = 0.0
    target_current: float = 0.0
    current_a: float = 0.0
    current_b: float = 0.0
    current_c: float = 0.0
    temp_motor: float = 0.0
    temp_inverter: float = 0.0
    rpm: int = 0
    target_rpm: int = 0
    pwm: int = 0
    target_pwm: int = 0
    controle_method: int = 0
    commutation: int = 0
    swish_freq: int = 0
    enable: int = 0
    pwm_p: int = 0
    pwm_i: int = 0
    pwm_d: int = 0