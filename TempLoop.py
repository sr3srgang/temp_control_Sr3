import numpy as np
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel, QPushButton
from PyQt5.QtCore import QTimer, QDateTime
from PlotWindow import PlotWindow
import os
from PID import PID

# for error handling
import sys
import traceback

# for typing
from typing import Union
from Keithley import Keithley, Keithley_mux
from Rigol import Rigol

# libraries for data uploading
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS


class TempLoop(QWidget):
    def __init__(self, title_name, input_device:Union[Keithley, Keithley_mux], output_device:Rigol, PID_params, channels, names):
        super(TempLoop, self).__init__()
        self.il = 0 # loop iteration #
        self.input_device = input_device
        self.output_device = output_device
        self.all_PID_params = PID_params
        self.n_loops = len(self.all_PID_params) #1
        self.all_PID = [PID(ps) for ps in self.all_PID_params]
        self.all_channels = channels
        self.all_names = names
        
        # Joon added: set rigol output to 12V
        # so that `turn_on_rigol_12V.py` doesn't have to be run
        # self.output_device.set_val(12)
        
        '''
        #MM removed integrator clearing option-- we never use this.
        #Adding option to clear integrator
        self.integrator_clear = QPushButton(self)
        self.integrator_clear.setText('Clear int.')
        self.integrator_clear.clicked.connect(self.clear_integrator)
        self.integrator_clear.move(250, 70)'''
        
        self.setWindowTitle(title_name)
        #Adding option to open pop-up plot
        self.plot_window = QPushButton(self)
        self.plot_window.setText('Show plot')
        self.plot_window.clicked.connect(self.make_window)
        #self.plot_window.move(250, 1)
        
        layout = QGridLayout()
        #Adding text for each loop
        self.setpoint_labels = []
        self.temp_labels = []
        self.voltage_labels = []
        self.time_label = QLabel("Time")
        layout.addWidget(self.time_label, 0, 0)
        layout.addWidget(self.plot_window, 0, 1)
        
        for k in np.arange(self.n_loops):
            self.setpoint_labels.append(QLabel("Loop setpoint: {}".format(self.all_PID_params[k]["setpoint"])))
            self.temp_labels.append(QLabel("Current temp: Not active"))
            self.voltage_labels.append(QLabel("Rigol V: {}".format(self.all_PID_params[k]["output_default"])))
            
            layout.addWidget(QLabel(self.all_names[k]), 2, k)
            layout.addWidget(self.setpoint_labels[k], 3, k)
            layout.addWidget(self.temp_labels[k], 4, k)
            layout.addWidget(self.voltage_labels[k], 5, k)
            
        self.setLayout(layout)
        
        #timer loop init
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_all_loops)
        self.timer.start(self.all_PID_params[0]["dt"]*1000)
        # Ensure first update happens immediately
        QTimer.singleShot(100, self.update_all_loops)
            
  
        #Setting up data log
        self.day = None
        self.f_path = None #"test_log_dev.txt"
        self.df_path = "/home/srgang/H/data/temp_logs"
        self.f_name = "_temp_log.txt"
        #
        
    def get_fname_write(self, dt):
        now = dt.toString('yyyy-MM-dd')
        if self.day != now:
            self.day = now
            folder_name = dt.toString('yyyyMMdd')
            folder_path = os.path.join(self.df_path, folder_name)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)
            this_file = folder_name + self.f_name 
            self.f_path = os.path.join(self.df_path, folder_name, this_file)
        return self.f_path
                     
    def make_window(self):
        fname_read = self.f_path
        self.pw = PlotWindow(fname_read)
        self.pw.show()
    
    #def clear_integrator(self):
        #self.PID.clear_integrator() 
        
    def update_all_loops(self):
        time = QDateTime.currentDateTime()
        timeDisplay=time.toString('yyyy-MM-dd hh:mm:ss dddd')
        self.time_label.setText(timeDisplay)
        for k in np.arange(self.n_loops):
    	    self.update_loop(k, time, timeDisplay)      
    	     
    def update_loop(self, k = 0, time = None, timeDisplay = None):
        #"k" index now specifies which loop to update
        print(k)
        try:
            #Read temp, update window, log. 
            ch = self.all_channels[k]
            #Read in value from Keithley,
            try:
                current_temp, res = self.input_device.read_temp(channel = ch["input_ch"])
            except Exception as ex:
                print("Get Keithley temp reading failed.", file=sys.stderr)
                print(traceback.format_exception(), file=sys.stderr)
                return
            self.temp_labels[k].setText("Current temp @ {}: {:.3f}".format(ch["input_ch"], current_temp))
            print(current_temp)
            #Log temp and output
            print(f"[{time.toString('MM/dd hh:mm:ss')}] {self.il}: [P,I,D]=", end="")
            output = self.all_PID[k].update(current_temp)
            f_path = self.get_fname_write(time)
            
            #To actuate:
            try:
                self.output_device.set_val(output, channel = ch["output_ch"])
            except Exception as ex:
                print("Set RIGOL output voltage failed.", file=sys.stderr)
                print(traceback.format_exception(), file=sys.stderr)
                return
                
            # write log to file
            try:
                with open(f_path, 'a') as f:
                    f.write("{}, {}, {}, {}, {}\n".format(timeDisplay, current_temp, res, output, k))
            except Exception as ex:
                print("Writing log to file faield.", file=sys.stderr)
                print(traceback.format_exception(), file=sys.stderr) 
            
            # Send result to influxdb
            try:
                with InfluxDBClient(url="http://yesnuffleupagus.colorado.edu:8086", token="yelabtoken", org="yelab", debug=False) as client:
                    write_api = client.write_api(write_options=SYNCHRONOUS)
                    write_api.write("data_logging", "yelab", "Sr3_temp,Channel=1 Value={}".format(current_temp))
            except Exception as ex:
                print("InfluxDB uploading failed.", file=sys.stderr)
                print(traceback.format_exception(), file=sys.stderr)
            

            self.voltage_labels[k].setText("Rigol Ch {} V: {:.3f}".format(ch["output_ch"], output))
        except Exception as ex:
            print("Unhandled exception raised. Dropping this iteration.", file=sys.stderr)
            print(traceback.format_exception(), file=sys.stderr)
            return
        finally:
            self.il = self.il + 1
