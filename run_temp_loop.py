import numpy as np
from TempLoop import TempLoop
import sys
from PyQt5.QtWidgets import QApplication
from Keithley import Keithley
from Rigol import Rigol

if __name__ == '__main__':
    app = QApplication(sys.argv)
    #PID_params = {"k_prop": -.35, "t_int": 60, "t_diff": 0, "setpoint":19.2,  "dt": 15, "output_default":2.5, "rails": [1, 5]}
    #MM 20221227 turned down gain from -.25 to -.2 bc servo was ringing. 
    PID_params = {"k_prop": -.15, "t_int": 120, "t_diff": 0, "setpoint":19.6,  "dt": 15, "output_default":1.4, "rails": [1, 5]}
    k = Keithley('192.168.1.25', 5025)
    r = Rigol('192.168.1.27', 5555, 2)  
    loop=TempLoop("Laser-side temp loop", k, r, PID_params)
    loop.show()
    sys.exit(app.exec_())
