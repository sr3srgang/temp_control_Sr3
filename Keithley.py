import socket
import numpy as np


class Keithley():
    """Reading the resistance (and hence the temp) of the thermistor connected to the front-panel input"""
    def __init__(self, ip_address, port):
        print(f"Connecting to Keithley: {ip_address}:{port}...")
        self.port = port
        self.buffer_size = 2048
        self.ip_address = ip_address
        
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.ip_address, self.port))
            self.send_msg(s, "*IDN?")
            response = s.recv(self.buffer_size)
            print("Connected!")
            print("\t" + f"\t response: *IDN? = {response}")
            
        except Exception as ex:
            raise ex
        
        
    
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

