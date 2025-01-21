""" guiHelper.py
This file contains the gui helper class.

@Author: Philipp Eilmann
"""

__version__ = "0.0.1"

from .uartHelper import  UartHelper
from .models.dataClasses import SystemData
from .models.uartDefines import CommutationsTypeValues, SwishFrequencyValues, ControlMethodValues, UpdateRates
import dearpygui.dearpygui as dpg
import dearpygui.demo as demo
import logging


logger = logging.getLogger(__name__)

class GuiHelper():
    """
    GuiHelper class to handle the GUI for the application.

    Attributes:
    -----------
    _systemData : SystemData
        An instance of SystemData containing system-wide data.
    _uartInstances : list
        A list of available UART instances.
    _minRPM : int
        The minimum RPM value.
    _maxRPM : int
        The maximum RPM value.
    _timeDisplayed : int
        The amount of time to display in the plots.
    _timeStamp : list
        A list of timestamps for the plots.
    _currentList0 : list
        A list of current values for phase 0.
    _currentListA : list
        A list of current values for phase A.
    _currentListB : list
        A list of current values for phase B.
    _currentListC : list
        A list of current values for phase C.
    _pwmListActual : list
        A list of actual PWM values.
    _pwmListTarget : list
        A list of target PWM values.
    _rpmListActual : list
        A list of actual RPM values.
    _rpmListTarget : list
        A list of target RPM values.
    _currenMax : float
        The maximum current value.
    _currenMin : float
        The minimum current value.
    _rpmMax : float
        The maximum RPM value.
    _rpmMin : float
        The minimum RPM value.
    _pwmMax : float
        The maximum PWM value.
    _pwmMin : float
        The minimum PWM value.

    Methods:
    --------
    __init__(uartHelper: UartHelper, systemData: SystemData) -> None:
        Initialize the GuiHelper class.
    
    writeLog(msg: str, Tx: bool = False, Rx: bool = False) -> None:
        Write a log message to the GUI.
    
    abentToPlot(value0: float, valueA: float, valueB: float, valueC: float, rpmTarget: float, rpmActual: float, pwmTarget: float, pwmActual: float) -> None:
        Update the plots with new values.
    
    startGui() -> None:
        Initialize and start the GUI.
    
    isGuiRunning() -> bool:
        Check if the GUI is running.
    
    updateData(data: SystemData) -> None:
        Update the data in the GUI.
    
    renderWindow() -> None:
        Render a new frame in the GUI.
    
    cleanUp() -> None:
        Clean up the GUI context.
    """
    _systemData = SystemData()
    _uartInstances:list = []
    _minRPM = 100
    _maxRPM = 15000
    _timeDisplayed = 100
    
    _timeStamp:list = [0]
    _currentList0:list = [0]
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
                if dpg.get_value("check_update_all"):
                    self._updateUartSignals()
        else:
            ret = self.uartHelper.disconnect()
            if ret:
                # connected to host.
                dpg.set_item_label(item=sender, label="Connect")
                dpg.set_axis_limits_auto(self._curetn_Yaxis)
                dpg.set_axis_limits_auto(self._rpm_Yaxis)
                dpg.set_axis_limits_auto(self._pwm_Yaxis)
                dpg.set_axis_limits_auto(self._curetn_Xaxis)
                dpg.set_axis_limits_auto(self._rpm_Xaxis)
                dpg.set_axis_limits_auto(self._pwm_Xaxis)
                
    def _updateUartInstances(self, sender):
        self._uartInstances = self.uartHelper.listInstances()
        dpg.set_value("uart_combo", self._uartInstances[-1])
    
    def _updateCommuation(self, sender):
        value = dpg.get_value(sender)
        self._systemData.uartSignals.commutation.write(CommutationsTypeValues[value])
        logger.debug(f"Update commutation to: {value}")
        
    def _updateSwishFrequency(self, sender):
        value = dpg.get_value(sender)
        self._systemData.uartSignals.swish_freq.write(SwishFrequencyValues[value])
        logger.debug(f"Update swish frequency to: {value}")
    
    def _updateControlMode(self, sender):
        value = dpg.get_value(sender)
        if value == "RPM Control":
            dpg.show_item(item="p_input")
            dpg.show_item(item="i_input")
            dpg.show_item(item="d_input")
            dpg.show_item(item="rpm_slider_name")
            dpg.show_item(item="rpm_slider")
            dpg.show_item(item="spacer_control")
            dpg.hide_item(item="pwm_slider_name")
            dpg.hide_item(item="pwm_slider")
        elif value == "Remote Control":
            dpg.hide_item(item="p_input")
            dpg.hide_item(item="i_input")
            dpg.hide_item(item="d_input")
            dpg.hide_item(item="rpm_slider_name")
            dpg.hide_item(item="rpm_slider")
            dpg.hide_item(item="spacer_control")
            dpg.hide_item(item="pwm_slider_name")
            dpg.hide_item(item="pwm_slider")
        else:
            dpg.hide_item(item="p_input")
            dpg.hide_item(item="i_input")
            dpg.hide_item(item="d_input")
            dpg.hide_item(item="rpm_slider_name")
            dpg.hide_item(item="rpm_slider")
            dpg.hide_item(item="spacer_control")
            dpg.show_item(item="pwm_slider_name")
            dpg.show_item(item="pwm_slider")
        self._systemData.uartSignals.controle_method.write(ControlMethodValues[value])
        logger.info(f"Update control mode to: {value}")
        
    def _updateCurrentPlot(self, valueA, valueB, valueC, value0):
        self._currenMax = max([self._currenMax, valueA, valueB, valueC, value0])
        self._currenMin = min([self._currenMin, valueA, valueB, valueC, value0])
        self._currentList0.append(value0)
        self._currentListA.append(valueA)
        self._currentListB.append(valueB)
        self._currentListC.append(valueC)
        dpg.set_value('plot_current_0', [self._timeStamp, self._currentList0])
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
        # just increment the time stamp, no real time (for now)
        self._timeStamp.append(self._timeStamp[-1]+1)
        # self._timeStamp.append(time.time())
        arraySize = len(self._timeStamp)
        if arraySize > self._timeDisplayed:
            dpg.set_axis_limits(self._curetn_Xaxis, self._timeStamp[arraySize-self._timeDisplayed] , self._timeStamp[-1])
            dpg.set_axis_limits(self._rpm_Xaxis, self._timeStamp[arraySize-self._timeDisplayed] , self._timeStamp[-1])
            dpg.set_axis_limits(self._pwm_Xaxis, self._timeStamp[arraySize-self._timeDisplayed] , self._timeStamp[-1])
        else:
            dpg.set_axis_limits(self._curetn_Xaxis, self._timeStamp[0] , self._timeStamp[-1])
            dpg.set_axis_limits(self._rpm_Xaxis, self._timeStamp[0] , self._timeStamp[-1])
            dpg.set_axis_limits(self._pwm_Xaxis, self._timeStamp[0] , self._timeStamp[-1])
        
    def _updateInfoTable(self):
        for signal in self._systemData.uartSignals:
            if type(signal.value) == float:
                dpg.set_value(f"info_{signal.name}", round(signal.value,3))
            else:
                dpg.set_value(f"info_{signal.name}", signal.value)
            
    def _updateUartSignals(self):
        for signal in self._systemData.uartSignals:
            signal.cyclic = dpg.get_value(f"check_{signal.name}")
            cycleTime = dpg.get_value(f"combo_{signal.name}")
            signal.cycleTime = UpdateRates[cycleTime]
            
    def _openAboutModal(self, sender):
        with dpg.window(label="About", width=300, height=200, modal=True,
                        pos=((dpg.get_viewport_width()/2)-150, (dpg.get_viewport_height()/2)-100)):
            dpg.add_text("BLDC control panel")
            dpg.add_text("Version: 0.0.1")
            dpg.add_text("Author: Philipp Eilmann")
            
    def _writeRpm(self, sender):
        value = dpg.get_value(sender)
        self._systemData.target_rpm = value
        self._systemData.uartSignals.rpm.write(value)
        logger.debug(f"Update RPM to: {value}")

    def _writePwm(self, sender):
        value = dpg.get_value(sender)
        self._systemData.target_pwm = value
        self._systemData.uartSignals.pwm.write(value)
        logger.debug(f"Update PWM to: {value}")
        
            
        
########################################################################   
# Public calsses
########################################################################
   
    def __init__(self, uartHelper:UartHelper, systemData:SystemData):
        self.uartHelper = uartHelper
        logger.info(f"Init version:{__version__}")
        self._systemData = systemData
        
        
    def writeLog(self, msg, Tx=False, Rx=False)-> None:
        
        if Tx:
            dpg.add_text(f"< |{msg}", parent=self.logWindow, tracked=True, track_offset=1.0)
        elif Rx:
            dpg.add_text(f"> |{msg}", parent=self.logWindow, tracked=True, track_offset=1.0)
        else:
            dpg.add_text(f"{msg}",color=(252,255,0), parent=self.logWindow, tracked=True, track_offset=1.0)
        
        dpg.bind_item_theme(dpg.last_item(), "log_text_theme")
        
    def abentToPlot(self, value0:float,
                    valueA:float, valueB:float, valueC:float,
                    rpmTarget:float, rpmActual:float,
                    pwmTarget:float,pwmActual:float):
        """
        Update the plots with new values.

        Args:
            value0 (float): The current value for phase 0.
            valueA (float): The current value for phase A.
            valueB (float): The current value for phase B.
            valueC (float): The current value for phase C.
            rpmTarget (float): The target RPM value.
            rpmActual (float): The actual RPM value.
            pwmTarget (float): The target PWM value.
            pwmActual (float): The actual PWM value.
        """
        self._updateTimeAxis()
        self._updateCurrentPlot(valueA, valueB, valueC, value0)
        self._updateRpmPlot(target=rpmTarget, actual=rpmActual)
        self._updatePwmPlot(target=pwmTarget, actual=pwmActual)
       
        
    def startGui(self) -> None:
        """
        Initialize and start the GUI.
        """
        
        self._uartInstances = self.uartHelper.listInstances()
        
        dpg.create_context()
        dpg.create_viewport(title='BLCD control panel', width=1000, height=800)
        dpg.setup_dearpygui()
        
        with dpg.theme(tag="log_text_theme"):
                with dpg.theme_component(dpg.mvText):
                    dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 1)
                    
        # add a font registry
        with dpg.font_registry():
            # first argument ids the path to the .ttf or .otf file
            default_font = dpg.add_font("resources/Helvetica.otf", 14)
            heading_font = dpg.add_font("resources/HelveticaBold.otf", 14)
            button_font = dpg.add_font("resources/HelveticaBold.otf", 13)
            buttonBig_font = dpg.add_font("resources/HelveticaBold.otf", 25)
            
        dpg.bind_font(default_font)
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

            with dpg.menu(label="Signals"):
                dpg.add_text("Cyclic Requests")
                dpg.bind_item_font(dpg.last_item(), heading_font)
                for signal in self._systemData.uartSignals:
                    with dpg.group(horizontal=True):
                        dpg.add_checkbox(label=signal.name, default_value=signal.cyclic, tag=f"check_{signal.name}")
                        default_value = list(UpdateRates.keys())[list(UpdateRates.values()).index(signal.cycleTime)]
                        dpg.add_combo(default_value=default_value, items=list(UpdateRates.keys()), tag=f"combo_{signal.name}" ,width=100)
                dpg.add_checkbox(label="Update all @ connect", default_value=self._systemData.updateSignalsAtConnect, tag="check_update_all")
                dpg.add_button(label="Update", width=200 ,callback=self._updateUartSignals)
                dpg.bind_item_font(dpg.last_item(), heading_font)    
                
            dpg.add_menu_item(label="Help", callback=self._print_me)
            dpg.add_menu_item(label="Demo", callback=lambda:demo.show_demo())
            dpg.add_menu_item(label="About", callback=self._openAboutModal)
                
        ######################################################################################
        # Settimgs window
        ######################################################################################
        with dpg.window(label="Settings", width=300, height=581, pos=(700,0), no_close=True):
            dpg.add_text("Select MCU", indent=15)
            dpg.bind_item_font(dpg.last_item(), heading_font)
            dpg.add_combo(self._uartInstances, default_value=self._uartInstances[-1], tag="uart_combo",  width=250, indent=15)
            with dpg.group(horizontal=True, indent=15):
                dpg.add_button(label="Connect", width=80 ,callback=self._connectToHost)
                dpg.bind_item_font(dpg.last_item(), button_font)
                dpg.add_button(label="Reload", width=80, callback=self._updateUartInstances)
            # dpg.add_spacer(height=5)
            
            dpg.add_text("Modulation", indent=15)
            dpg.bind_item_font(dpg.last_item(), heading_font)
            dpg.add_combo(list(CommutationsTypeValues.keys()), 
                          default_value=list(CommutationsTypeValues.keys())[0],
                          tag="modulation_combo", width=250, indent=15, 
                          callback=self._updateCommuation)
            # dpg.add_spacer(height=5)
            
            dpg.add_text("Swish Frequency", indent=15)
            dpg.bind_item_font(dpg.last_item(), heading_font)
            dpg.add_combo(list(SwishFrequencyValues.keys()),
                          default_value=list(SwishFrequencyValues.keys())[0],
                          tag="frequency_combo", width=250, indent=15, 
                          callback=self._updateSwishFrequency)
            # dpg.add_spacer(height=5)
            
            dpg.add_text("Control Method", indent=15)
            dpg.bind_item_font(dpg.last_item(), heading_font)
            dpg.add_combo(list(ControlMethodValues.keys()),
                          default_value=list(ControlMethodValues.keys())[0],
                          tag="control_combo", width=250, indent=15, 
                          callback=self._updateControlMode)
            ## Closed loop
            dpg.add_spacer(height=5, show=False, tag="spacer_control")
            dpg.add_input_float(label="P Value", tag="p_input", indent=30, show=False, 
                                callback=lambda: self._systemData.uartSignals.p.write(dpg.get_value("p_input")))
            dpg.add_input_float(label="I Value", tag="i_input", indent=30, show=False, 
                                callback=lambda: self._systemData.uartSignals.i.write(dpg.get_value("i_input")))
            dpg.add_input_float(label="D Value", tag="d_input", indent=30, show=False,
                                callback=lambda: self._systemData.uartSignals.d.write(dpg.get_value("d_input")))
            
            dpg.add_spacer(height=5)
            dpg.add_text("RPM value", tag="rpm_slider_name", indent=15)
            dpg.add_drag_int(tag="rpm_slider", speed=50, tracked=True, format="%d%rpm", 
                             width=250, indent=15, min_value=self._minRPM, max_value=self._maxRPM, 
                             show=False, callback= self._writeRpm)
            
            ## Open loop
            dpg.add_text("PWM value", tag="pwm_slider_name", show=False, indent=15)
            dpg.add_drag_int(tag="pwm_slider", speed=0.5, tracked=True, format="%d%%", width=250, 
                             indent=15, min_value=0, max_value=100, 
                             callback= self._writePwm)
            
            
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
            
            dpg.add_spacer(height=15)
            dpg.add_button(label="Start", width=200, indent=50, height=35, tag="start_button",
                           callback=lambda: self._systemData.uartSignals.enable.write(1))
            dpg.bind_item_theme(dpg.last_item(), "start_button_theme")
            dpg.bind_item_font("start_button", buttonBig_font)
            dpg.add_button(label="Stop", width=200, indent=50, height=35, tag="stop_button",
                           callback=lambda: self._systemData.uartSignals.enable.write(0))
            dpg.bind_item_theme(dpg.last_item(), "stop_button_theme")
            dpg.bind_item_font("stop_button", buttonBig_font)

        ######################################################################################
        # Info window
        ######################################################################################
        with dpg.window(label="Info", width=300, height=200, pos=(700,600), no_close=True):
            with dpg.table(header_row=False, row_background=True, delay_search=True, tag="table_info"):
                dpg.add_table_column(width=220, width_fixed=True)
                dpg.add_table_column(width=80, width_fixed=True)
                dpg.add_table_column(width=50, width_fixed=True)
                for signal in self._systemData.uartSignals:
                    with dpg.table_row():
                        dpg.add_text(f"{signal.name}")
                        dpg.add_text(f"{signal.value}", tag=f"info_{signal.name}")
                        dpg.add_text(f"{signal.unite}")
                
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
                    
                with dpg.plot(label="Current", zoom_mod=0.5):
                    dpg.add_plot_legend()
                    self._curetn_Xaxis = dpg.add_plot_axis(dpg.mvXAxis, label="", no_tick_labels=True)
                    with dpg.plot_axis(dpg.mvYAxis, label="Current (A)", no_tick_labels=False) as self._curetn_Yaxis:
                        dpg.add_line_series(self._timeStamp, self._currentList0, label="Current DC", tag="plot_current_0")
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
        """
        Check if the GUI is running.

        Returns:
            bool: True if the GUI is running, False otherwise.
        """
        return dpg.is_dearpygui_running()
    
    def updateData(self, data:SystemData):
        """
        Update the data in the GUI.

        Args:
            data (SystemData): The data to update.
        """
        self._systemData = data
        self.abentToPlot(value0=data.uartSignals.current_0.value, 
                         valueA=data.uartSignals.current_a.value, 
                         valueB=data.uartSignals.current_b.value, 
                         valueC=data.uartSignals.current_c.value,
                         rpmTarget=data.target_rpm, 
                         rpmActual=data.uartSignals.rpm.value,
                         pwmTarget=data.target_pwm, 
                         pwmActual=data.uartSignals.pwm.value)
        self._updateInfoTable()
        try:
            value = list(CommutationsTypeValues.keys())[list(CommutationsTypeValues.values()).index(data.uartSignals.commutation.value)]
            dpg.set_value("modulation_combo", value)
        except:
            pass
        try:
            value = list(ControlMethodValues.keys())[list(ControlMethodValues.values()).index(data.uartSignals.controle_method.value)]
            dpg.set_value("control_combo", value)
        except:
            pass
        try:
            value = list(SwishFrequencyValues.keys())[list(SwishFrequencyValues.values()).index(data.uartSignals.swish_freq.value)]
            dpg.set_value("frequency_combo", value)
        except:
            pass
        
        
    def renderWindow(self):
        """ This will reander a new frame
        """
        dpg.render_dearpygui_frame()
    
    def cleanUp(self):
        """ This will clean up the class 
        """
        dpg.destroy_context()
        logger.info("Clean up done")