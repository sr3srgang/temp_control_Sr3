import numpy as np
from TempLoop import TempLoop
import sys
from PyQt5.QtWidgets import QApplication
from Keithley import Keithley
from Rigol import Rigol

if __name__ == '__main__':
    app = QApplication(sys.argv)
    PID_params = {"k_prop": -.35, "t_int": 50, "t_diff": 0, "setpoint":19.0,  "dt": 15, "output_default":1.53}
    #changed params at 9:12 am 
    #Made even more aggressive at 12:55
    #Seems to have destabilized-- relaxing slightly more at 12:33
    #increased derivative term at 5:37
    k = Keithley('192.168.1.25', 5025)
    r = Rigol('192.168.1.27', 5555, 2)  
    loop=TempLoop("Laser-side temp loop", k, r, PID_params)
    loop.show()
    sys.exit(app.exec_())
