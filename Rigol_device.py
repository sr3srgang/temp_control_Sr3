import socket
import time, datetime
import os
import numpy as np
from Rigol import Rigol

r = Rigol('10.1.140.242', 5555, 2) 
r.set_val(1)
