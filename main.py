"""main.py

    BLDC Inverter GUI
    
    This file init the Program.
    
    
"""
__author__ = "Philipp Eilmann"
__version__ = "0.0.1"

from moduls.guiHelper import GuiHelper
from moduls.uartHelper import UartHelper
import logging
import atexit
import schedule
import random


if __name__ == "__main__":
    """ Main function
    """
    
    #logger = logging.getLogger(__name__)
    logging.basicConfig(level=logging.INFO)
    
    uart = UartHelper()
    gui = GuiHelper(uart)

    gui.startGui()
    
    @atexit.register
    def cleanUp():
        uart.cleanUp()
        gui.cleanUp()
        
    lastPwm=0
    lastRpm=0
    targetPwm = 50
    targetRpm = 5000
    counter = 0
        
    def updatePlot():
        global lastPwm, lastRpm, targetPwm, targetRpm, counter
        valueBase = random.normalvariate(3.5, 1)
        valueA = random.uniform(-3.7,0.5)
        valueB = random.uniform(-0.5,0.5)
        valueC = random.uniform(-0.5,0.5)
        
        error = targetPwm-lastPwm
        lastPwm = lastPwm + 0.2*error

        error = targetRpm-lastRpm
        lastRpm = lastRpm + 0.2*error
        
        gui.abentToPlot(
            valueA=valueBase+valueA, 
            valueB=valueBase+valueB, 
            valueC=valueBase+valueC,
            rpmActual=lastRpm, rpmTarget=targetRpm,
            pwmActual=lastPwm, pwmTarget=targetPwm
            )
        if counter > 10:
            return schedule.CancelJob
    
        #counter += 1
    
    schedule.every().seconds.do(updatePlot)
        

    while gui.isGuiRunning():
        # insert here any code you would like to run in the render loop
        # you can manually stop by using stop_dearpygui()
        # print("this will run every frame")
        gui.renderWindow()
        schedule.run_pending()
    
