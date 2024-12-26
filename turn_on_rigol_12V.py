import socket
import time, datetime
import os
import numpy as np
from Rigol import Rigol

r = Rigol('192.168.1.27', 5555, 1, 12.1) 
r.set_val(12)

