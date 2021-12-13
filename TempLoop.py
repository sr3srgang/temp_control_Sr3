import numpy as np
from PyQt5.QtWidgets import QWidget, QGridLayout, QLabel
from PyQt5.QtCore import QTimer, QDateTime

class TempLoop(QWidget):
    def __init__(self, name, input_device, output_device, PID_params):
        super(TempLoop, self).__init__()
        
        self.input_device = input_device
        self.output_device = output_device
        self.PID_params = PID_params
        
        self.setWindowTitle(name)
                
        self.setpoint_label = QLabel("Loop setpoint: {}".format(self.PID_params["setpoint"]))
        self.temp_label = QLabel("Current temp: Not active")
        self.time_label = QLabel("Time")
        
        layout = QGridLayout()
        layout.addWidget(self.time_label, 0, 0)
        layout.addWidget(self.setpoint_label, 1, 0)
        layout.addWidget(self.temp_label, 1, 1)
        self.setLayout(layout)
        
        self.loop_time = self.PID_params["dt"]
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_loop)
        self.timer.start(self.loop_time*1000)
        
        #Setting up data log
        self.f_path = "test_log.txt"
        f = open(self.f_path, 'w')
        
    def update_loop(self):
        #Read temp, update window, log. 
        time = QDateTime.currentDateTime()
        timeDisplay=time.toString('yyyy-MM-dd hh:mm:ss dddd')
        self.time_label.setText(timeDisplay)
        current_temp, res = self.input_device.read_temp()
        self.temp_label.setText("Current temp: {:.1f}".format(current_temp))
        with open(self.f_path, 'a') as f:
            f.write("{}, {}, {}\n".format(timeDisplay, current_temp, res))
        
           
        #TODO: PID loop and actuate on Rigol
            
