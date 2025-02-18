import numpy as np
from TempLoop import TempLoop
import sys
from PyQt5.QtWidgets import QApplication
from Keithley import Keithley, Keithley_mux
from Rigol import Rigol

if __name__ == '__main__':
    app = QApplication(sys.argv)
    #PID_params = {"k_prop": -.35, "t_int": 60, "t_diff": 0, "setpoint":19.2,  "dt": 15, "output_default":2.5, "rails": [1, 5]}
    #MM 20221227 turned down gain from -.25 to -.2 bc servo was ringing. 
    #PID_params = {"k_prop": -.15, "t_int": 120, "t_diff": 0, "setpoint":19.6,  "dt": 15, "output_default":1.53, "rails": [1, 5]}
    # 20241226 JH increased set temp to lower the PCW flow to the HEPA; it was dominating the PCW for Sr3
    PID_params = {"k_prop": -.15, "t_int": 120, "t_diff": 0, "setpoint":20.5,  "dt": 15, "output_default":1.53, "rails": [1, 5]}
    # k = Keithley_mux('192.168.1.25', 5025) # for a resister in the front-panel
    k = Keithley_mux('192.168.1.25', 5025) # rear panel
    r = Rigol('192.168.1.27', 5555, 2)  
    loop=TempLoop("Laser-side temp loop", k, r, PID_params)
    loop.show()
    sys.exit(app.exec_())
