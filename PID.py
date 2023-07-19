import numpy as np

class PID:
    '''
    Accepts an error signal and calculates  
    Note: error signal extracted separately from devices for more modular code
    '''
    
    def __init__(self, params):
        '''
        Params:
        k_prop: Proportional gain coefficient
        t_int: Integration time
        t_diff: Differentiation time
        setpoint: The setpoint of the control variable
        dt: How often to refresh the control loop (sec)
        output_default: zero-point for output signal'''
        self.params = params
        
        self.current_reading = np.nan
        self.last_reading = np.nan
        
        self.integral_value = 0
        self.error_value = np.nan
        
        
    def is_safe_val(self, output_sig):
        rails = self.params["rails"]
        return (output_sig > rails[0]) and (output_sig < rails[1])
    
    def get_safe_val(self, output_sig):
        rails = self.params["rails"]
        if rails[0] > output_sig:
            return rails[0]
        else:
            return min(rails[1], output_sig)
            
    def output_signal(self):
        k = self.params["k_prop"]
        prop = k*self.error_value
        integral = k*self.integral_value
        diff = k*(self.current_reading - self.last_reading)*self.params["t_diff"]/self.params["dt"]
        print([prop, integral, diff])
        return prop + integral + diff + self.params["output_default"]
        
    def update(self, reading):
        self.last_reading = self.current_reading
        self.current_reading = reading
        
        #Avoid issues while starting up the loop
        if not (np.isnan(self.current_reading)) and not (np.isnan(self.last_reading)):
           self.error_value = self.params["setpoint"] - self.current_reading
           new_int = self.integral_value + self.error_value*self.params["dt"]/self.params["t_int"]
           new_output = self.output_signal()
           if self.is_safe_val(new_output):
               self.integral_value = new_int
               return new_output
           else:
               #Note that here we DON'T update the integrator to avoid further wind-up
               return self.get_safe_val(new_output)
        else:
           return self.params["output_default"]    
    
    def clear_integrator(self):
    	#useful when tuning loop to clear integrator wind-up
        self.integral_value = 0  
            
        
