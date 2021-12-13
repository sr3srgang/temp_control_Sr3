import numpy as np
from TempLoop import TempLoop
import sys
from PyQt5.QtWidgets import QApplication
from Keithley import Keithley

if __name__ == '__main__':
    app = QApplication(sys.argv)
    PID_params = {"setpoint": 30, "dt": 5}
    k = Keithley('192.168.1.25', 5025) 
    loop=TempLoop("Laser-side temp loop", k, None, PID_params)
    loop.show()
    sys.exit(app.exec_())
