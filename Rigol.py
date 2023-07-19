import socket
import numpy as np

class Rigol():

    def __init__(self, ip_address, port, channel, vMax = 5):
        self.port = port
        self.ip_address = ip_address
        self.channel = channel
        self.vMax = vMax
        self.vMin = 1
        self.power_channel = 1 #MM 20221229 check to turn power on if you hit a rail, just in case there was a power blip. 
        self.power_value = 12
	
    def send_msg(self, s, msg):
        encoded = msg.encode('utf-8')
        s.send(encoded)
            
    def set_val(self, V, channel = None, vMax = 12.1):
        if channel is None:
            channel = self.channel
            vMax = self.vMax   
        if (V is not None) and (V > self.vMin) and (V < vMax):
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((self.ip_address, self.port))
        
            set_channel = ':INST CH' + str(channel) +'\n'
            set_voltage = ':VOLT ' + str(V) + '\n'
            set_on = ':OUTP CH' + str(channel) + ',ON \n'
            msgs = [set_channel, set_voltage, set_on]
        
            for m in msgs:
                self.send_msg(s, m)
        else:
            print("Invalid voltage value {}".format(V))
            self.set_val(self.power_value, self.power_channel)
            print("Reset power to valve.")
           
    def read_val(self, V):
        pass
