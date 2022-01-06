import socket
import numpy as np


class Keithley():

    def __init__(self, ip_address, port):
        self.port = port
        self.buffer_size = 2048
        self.ip_address = ip_address
    
    def send_msg(self, s, msg):
        encoded = msg.encode('utf-8')
        s.send(encoded)
        
    def read_resistance(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((self.ip_address, self.port))
        msgs = (["*RST \n", 
            "FUNC 'RES' \n",
            "READ? \n"])
        for m in msgs:
            self.send_msg(s, m)
        
        return float(s.recv(self.buffer_size))
        
    def read_temp(self):
        resistance = self.read_resistance()
        local_slope = 1/(-1.7e+3) #1 degree per 1.7 kOhm in neighborhood of 22C, 33 kOhm
        temp = (resistance-40.77e+3)*local_slope + 18 #44008RC thermistor
        return temp, resistance

