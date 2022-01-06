import socket
import numpy as np

class Rigol():

    def __init__(self, ip_address, port, channel):
        self.port = port
        self.ip_address = ip_address
        self.channel = channel
        self.vMax = 5
        self.vMin = 1

    def send_msg(self, s, msg):
        encoded = msg.encode('utf-8')
        s.send(encoded)
            
    def set_val(self, V):
        if (V is not None) and (V > self.vMin) and (V < self.vMax):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.ip_address, self.port))
        
            set_channel = ':INST CH' + str(self.channel) +'\n'
            set_voltage = ':VOLT ' + str(V) + '\n'
            set_on = ':OUTP CH' + str(self.channel) + ',ON \n'
            msgs = [set_channel, set_voltage, set_on]
        
            for m in msgs:
                self.send_msg(s, m)
        else:
            print("Invalid voltage value {}".format(V))
           
    def read_val(self, V):
        pass
