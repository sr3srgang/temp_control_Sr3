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

class Keithley_mux():
    """Reading the resistance (and hence the temp) of 
    the thermistor connected to a channel of 7701 Multiplexer
    
    Current channel: 101 (Ch1 in the multiplexer inserted in
    Slot 1 of Keithely DAQ610)"""
    
    def __init__(self, ip_address, port):
        self.port = port
        self.buffer_size = 2048
        self.ip_address = ip_address

        # test connection
        print(f"Test connection to Keithley: {ip_address}:{port}...")
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(1) # s 
            s.connect((self.ip_address, self.port))
            self.send_msg(s, "*IDN?\n")
            response = s.recv(self.buffer_size)
            print("Connected!")
            print(rf"response: *IDN? = {response}")
            
        except Exception as ex:
            raise ex
        
        # print("Keithley_mux() object initiated")
        
    
    def send_msg(self, s, msg):
        encoded = msg.encode('utf-8')
        s.send(encoded)
        # print(f"\tSending to Keithley: {msg}")
        
    def read_resistance(self, channel ='101'):
        # print(f"Attemp to read resistance...")
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1) # s 
        s.connect((self.ip_address, self.port))
        
        # Updated SCPI commands for CH101 on the 7701 multiplexer
        msgs = ([
            "*RST \n", 
            "SENS:FUNC 'RES',(@{}) \n".format(channel),  # Set function to resistance on CH101
            "SENS:RES:RANG 100000,(@{}) \n".format(channel),  # Set fixed range (100 kΩ)
            "SENS:RES:NPLC 1,(@{}) \n".format(channel),  # Set integration time (faster)
            "ROUT:SCAN (@{}) \n".format(channel),  # Set scan to channel 101 (fixed)
            "INIT \n",  # Start measurement
            "*WAI \n",
            "FETC? \n"  # Fetch the measured resistance
        ])


        for m in msgs:
            self.send_msg(s, m)

        msg_recv = s.recv(self.buffer_size)
        # print(f"\tRecieved from Keithley: {msg_recv}")
        return float(msg_recv)
        # return float(s.recv(self.buffer_size))
        
        
    def read_temp(self, channel = '101'):
        resistance = self.read_resistance(channel)
        local_slope = 1/(-1.7e+3) #1 degree per 1.7 kOhm in neighborhood of 22C, 33 kOhm
        temp = (resistance-40.77e+3)*local_slope + 18 #44008RC thermistor
        return temp, resistance

