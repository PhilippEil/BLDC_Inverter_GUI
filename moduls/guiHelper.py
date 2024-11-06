"""guiHelper.py
 

"""

__author__ = "Philipp Eilmann"
__version__ = "0.0.1"

import dearpygui.dearpygui as dpg
import dearpygui.demo as demo
from .uartHelper import  UartHelper
import logging

logger = logging.getLogger(__name__)

class GuiHelper( ):
    
    _uartInstances:list = []
    _modulationList:list =["Blockkomutirung 120", "Blockkomutirung 180"]
    _minRPM = 100
    _maxRPM = 15000
    
    _timeStamp:list = [0]
    _currentListA:list = [0]
    _currentListB:list = [0]
    _currentListC:list = [0]
    _pwmListActual:list = [0]
    _pwmListTarget:list = [0]
    _rpmListActual:list = [0]
    _rpmListTarget:list = [0]
    _currenMax:float = 0.0
    _currenMin:float = 0.0
    _rpmMax:float = 0.0
    _rpmMin:float = 0.0
    _pwmMax:float = 0.0
    _pwmMin:float = 0.0
    
########################################################################   
# Private calsses
########################################################################   
    def _print_me(self, sender):
        logger.info(f"Menu Item: {sender}")
    
    def _save_init(self):
        dpg.save_init_file("dpg.ini")
        
    def _load_init(self, reset=True):
        #dpg.set_item_pos()
        dpg.configure_app(init_file="dpg.ini")  # default file is 'dpg.ini'
        
    def _connectToHost(self, sender):
        buttonLabel = dpg.get_item_label(sender)
        logger.info(f"presst button: {sender = } {buttonLabel = }")
        if buttonLabel == "Connect":
            instance = dpg.get_value("uart_combo")
            ret = self.uartHelper.connect(instance)
            if ret:
                # connected to host.
                dpg.set_item_label(item=sender, label="Disconnect")
        else:
            ret = self.uartHelper.disconnect()
            if ret:
                # connected to host.
                dpg.set_item_label(item=sender, label="Connect")
    
    def _updatePWM(self, sender):
        value = dpg.get_value(sender)
        logger.info(f"Update pwm to: {value}")
        self.writeLog(f"Update pwm to: {value}")
    
    def _changeControlMode(self, sender):
        value = dpg.get_value(sender)
        if value == "Closed loop":
            dpg.show_item(item="p_input")
            dpg.show_item(item="i_input")
            dpg.show_item(item="d_input")
            dpg.show_item(item="rpm_slider_name")
            dpg.show_item(item="rpm_slider")
            dpg.hide_item(item="pwm_slider_name")
            dpg.hide_item(item="pwm_slider")
        else:
            dpg.hide_item(item="p_input")
            dpg.hide_item(item="i_input")
            dpg.hide_item(item="d_input")
            dpg.hide_item(item="rpm_slider_name")
            dpg.hide_item(item="rpm_slider")
            dpg.show_item(item="pwm_slider_name")
            dpg.show_item(item="pwm_slider")
            
            
        logger.info(f"Update control mode to: {value}")
        
    def _updateCurrentPlot(self, valueA, valueB, valueC):
        self._currenMax = max([self._currenMax, valueA, valueB, valueC])
        self._currenMin = min([self._currenMin, valueA, valueB, valueC])
        self._currentListA.append(valueA)
        self._currentListB.append(valueB)
        self._currentListC.append(valueC)
        dpg.set_value('plot_current_a', [self._timeStamp, self._currentListA])
        dpg.set_value('plot_current_b', [self._timeStamp, self._currentListB])
        dpg.set_value('plot_current_c', [self._timeStamp, self._currentListC])
        dpg.set_axis_limits(self._curetn_Yaxis, self._currenMin*1.05, self._currenMax*1.05)
        
    
    def _updateRpmPlot(self, target, actual):
        self._rpmMax = max([self._rpmMax, target, actual])
        self._rpmMin = min([self._rpmMin, target, actual])
        self._rpmListTarget.append(target)
        self._rpmListActual.append(actual)
        dpg.set_value('plot_rpm_target', [self._timeStamp, self._rpmListTarget])
        dpg.set_value('plot_rpm_actual', [self._timeStamp, self._rpmListActual])
        dpg.set_axis_limits(self._rpm_Yaxis, self._rpmMin*1.05, self._rpmMax*1.05)
        
    def _updatePwmPlot(self, target, actual):
        self._pwmMax = max([self._pwmMax, target, actual])
        self._pwmMin = min([self._pwmMin, target, actual])
        self._pwmListTarget.append(target)
        self._pwmListActual.append(actual)
        dpg.set_value('plot_pwm_target', [self._timeStamp, self._pwmListTarget])
        dpg.set_value('plot_pwm_actual', [self._timeStamp, self._pwmListActual])
        dpg.set_axis_limits(self._pwm_Yaxis, self._pwmMin*1.05, self._pwmMax*1.05)
    
    def _updateTimeAxis(self):
        self._timeStamp.append(self._timeStamp[-1]+1)
        if len(self._timeStamp) > 100:
            dpg.set_axis_limits(self._curetn_Xaxis, self._timeStamp[-100] , self._timeStamp[-1])
            dpg.set_axis_limits(self._rpm_Xaxis, self._timeStamp[-100] , self._timeStamp[-1])
            dpg.set_axis_limits(self._pwm_Xaxis, self._timeStamp[-100] , self._timeStamp[-1])
        else:
            dpg.set_axis_limits(self._curetn_Xaxis, self._timeStamp[0] , self._timeStamp[-1])
            dpg.set_axis_limits(self._rpm_Xaxis, self._timeStamp[0] , self._timeStamp[-1])
            dpg.set_axis_limits(self._pwm_Xaxis, self._timeStamp[0] , self._timeStamp[-1])
        
        
########################################################################   
# Public calsses
########################################################################
   
    def __init__(self, uartHelper:UartHelper):
        self.uartHelper = uartHelper
        logger.info(f"Init version:{__version__}")
        
    def writeLog(self, msg, Tx=False, Rx=False)-> None:
        
        if Tx:
            dpg.add_text(f"< |{msg}", parent=self.logWindow, tracked=True, track_offset=1.0)
        elif Rx:
            dpg.add_text(f"> |{msg}", parent=self.logWindow, tracked=True, track_offset=1.0)
        else:
            dpg.add_text(f"{msg}",color=(252,255,0), parent=self.logWindow, tracked=True, track_offset=1.0)
        
        dpg.bind_item_theme(dpg.last_item(), "log_text_theme")
        
    def abentToPlot(self, 
                    valueA:float, valueB:float, valueC:float,
                    rpmTarget:float, rpmActual:float,
                    pwmTarget:float,pwmActual:float):
        logger.info(f"Add to plot: {pwmTarget =} {pwmActual =} ")
        self._updateTimeAxis()
        self._updateCurrentPlot(valueA, valueB, valueC)
        self._updateRpmPlot(target=rpmTarget, actual=rpmActual)
        self._updatePwmPlot(target=pwmTarget, actual=pwmActual)
       
        
    def startGui(self) -> None:
        """Inizilices and starts the window
        """
        
        self._uartInstances = self.uartHelper.listInstances()
        
        dpg.create_context()
        dpg.create_viewport(title='BLCD control panel', width=1000, height=800)
        dpg.setup_dearpygui()
        
        with dpg.theme(tag="log_text_theme"):
                with dpg.theme_component(dpg.mvText):
                    dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 1)
        
        #dpg.configure_app(init_file="dpg.ini")  # default file is 'dpg.ini'
        
        ######################################################################################
        # Navbare
        ######################################################################################
        with dpg.viewport_menu_bar():
            with dpg.menu(label="File"):
                dpg.add_menu_item(label="Save", callback=self._print_me)
                dpg.add_menu_item(label="Save As", callback=self._print_me)

            with dpg.menu(label="Window"):
                dpg.add_menu_item(label="Reset Window", callback=self._load_init)
                dpg.add_menu_item(label="Save Window", callback=self._save_init)
                dpg.add_menu_item(label="Load Window", callback=self._save_init)

            dpg.add_menu_item(label="Help", callback=self._print_me)
            dpg.add_menu_item(label="Demo", callback=lambda:demo.show_demo())

            with dpg.menu(label="Widget Items"):
                dpg.add_checkbox(label="Pick Me", callback=self._print_me)
                dpg.add_button(label="Press Me", callback=self._print_me)
                dpg.add_color_picker(label="Color Me", callback=self._print_me)
                
        ######################################################################################
        # Settimgs window
        ######################################################################################
        with dpg.window(label="Settings", width=300, height=800, pos=(700,0), no_close=True):
            dpg.add_text("Select MCU", indent=15)
            dpg.add_combo(self._uartInstances, tag="uart_combo",  width=250, indent=15)
            dpg.add_button(label="Connect", callback=self._connectToHost, indent=15)
            dpg.add_spacer(height=30)
            
            dpg.add_text("Select Modulation", indent=15)
            dpg.add_combo(self._modulationList, tag="modulation_combo", width=250, indent=15)
            dpg.add_spacer(height=15)
            
            dpg.add_radio_button(("Open loop", "Closed loop"), callback=self._changeControlMode)
            ## Closed loop
            dpg.add_input_float(label="P Value", tag="p_input", indent=30, show=False)
            dpg.add_input_float(label="I Value", tag="i_input", indent=30, show=False)
            dpg.add_input_float(label="D Value", tag="d_input", indent=30, show=False)
            
            dpg.add_spacer(height=15)
            dpg.add_text("RPM value", tag="rpm_slider_name", indent=15)
            dpg.add_drag_int(tag="rpm_slider", speed=50, tracked=True, format="%d%rpm", 
                             width=250, indent=15, min_value=self._minRPM, max_value=self._maxRPM, 
                             show=False, callback=self._updatePWM)
            
            ## Open loop
            dpg.add_text("PWM value", tag="pwm_slider_name", show=False, indent=15)
            dpg.add_drag_int(tag="pwm_slider", speed=0.5, tracked=True, format="%d%%", width=250, 
                             indent=15, callback=self._updatePWM)
            
            dpg.add_spacer(height=50)
            with dpg.theme(tag="start_button_theme"):
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, (0, 195, 17))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (7.0, 0.7, 0.7))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (112, 197, 120))
                    #dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, i*5)
                    #dpg.add_theme_style(dpg.mvStyleVar_FramePadding, i*3, i*3)
            
            with dpg.theme(tag="stop_button_theme"):
                with dpg.theme_component(dpg.mvButton):
                    dpg.add_theme_color(dpg.mvThemeCol_Button, (195, 0, 0))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, (7.0, 0.7, 0.7))
                    dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, (197, 112, 112))
                    #dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, i*5)
                    #dpg.add_theme_style(dpg.mvStyleVar_FramePadding, i*3, i*3)
            
            dpg.add_button(label="Start", width=200, indent=50, height=35)
            dpg.bind_item_theme(dpg.last_item(), "start_button_theme")
            dpg.add_button(label="Stop", width=200, indent=50, height=35)
            dpg.bind_item_theme(dpg.last_item(), "stop_button_theme")
        
        ######################################################################################  
        # Plot window 
        ######################################################################################
        with dpg.window(label="Plots", width=700, height=581, pos=(0,0), no_close=True):
            with dpg.subplots(3, 1, label="My Subplots", width=-1, height=-1, row_ratios=[1.0, 1.0, 1.0], no_title=True) as subplot_id:

                with dpg.plot(label="PWM"):
                    dpg.add_plot_legend()
                    self._pwm_Xaxis = dpg.add_plot_axis(dpg.mvXAxis, label="", no_tick_labels=True)
                    with dpg.plot_axis(dpg.mvYAxis, label="", no_tick_labels=False) as self._pwm_Yaxis:
                        dpg.add_line_series(self._timeStamp, self._pwmListTarget, label="Target", tag="plot_pwm_target")
                        dpg.add_line_series(self._timeStamp, self._pwmListActual, label="Actual", tag="plot_pwm_actual")
                    
                with dpg.plot(label="RPM"):
                    dpg.add_plot_legend()
                    self._rpm_Xaxis = dpg.add_plot_axis(dpg.mvXAxis, label="", no_tick_labels=True)
                    with dpg.plot_axis(dpg.mvYAxis, label="", no_tick_labels=False) as self._rpm_Yaxis :
                        dpg.add_line_series(self._timeStamp, self._rpmListTarget, label="Target", tag="plot_rpm_target")
                        dpg.add_line_series(self._timeStamp, self._rpmListActual, label="Actual", tag="plot_rpm_actual")    
                    
                with dpg.plot(label="Current", pan_mod=2):
                    dpg.add_plot_legend()
                    self._curetn_Xaxis = dpg.add_plot_axis(dpg.mvXAxis, label="", no_tick_labels=True)
                    with dpg.plot_axis(dpg.mvYAxis, label="Current (A)", no_tick_labels=False) as self._curetn_Yaxis:
                        dpg.add_line_series(self._timeStamp, self._currentListA, label="Current A", tag="plot_current_a")
                        dpg.add_line_series(self._timeStamp, self._currentListA, label="Current B", tag="plot_current_b")
                        dpg.add_line_series(self._timeStamp, self._currentListA, label="Current C", tag="plot_current_c")
            
            
        
        ######################################################################################    
        # Log window
        ######################################################################################
        with dpg.window(label="Log", width=700, height=200, pos=(0,600), no_close=True) as self.logWindow:
            pass
            
        
        dpg.show_viewport()
        
        
    def isGuiRunning(self)-> bool:
        """Get the state of the window

        Returns:
            bool: true if the dearpygui is running
        """
        return dpg.is_dearpygui_running()
    
    def renderWindow(self):
        """ This will reander a new frame
        """
        dpg.render_dearpygui_frame()
    
    def cleanUp(self):
        """ This will clean up the class 
        """
        dpg.destroy_context()
        logger.info("Clean up done")