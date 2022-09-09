# BMP180 class
import math
import random
import urequests
import json


class BMP180():
    '''
    Mock Module for the BMP180 pressure sensor.
    Behaves like the BMP180 library to be used as a drop in replacement
    '''
    # init
    def __init__(self, i2c_bus):
        with open('config.json') as config_file:
            config = json.load(config_file)
        if config['mock_endpoint'] != "":
            self.endpoint = f"{config['mock_endpoint']}{config['node_name']}/"
        else:
            self.endpoint = "" 
        # settings to be adjusted by user
        self.oversample_setting = 3
        self.baseline = 101325.0



    @property
    def oversample_sett(self):
        return self.oversample_setting

    @oversample_sett.setter
    def oversample_sett(self, value):
        if value in range(4):
            self.oversample_setting = value
        else:
            print('oversample_sett can only be 0, 1, 2 or 3, using 3 instead')
            self.oversample_setting = 3

    @property
    def temperature(self):
        '''
        Temperature in degree C.
        '''
        
        if self.endpoint != "":
            response = urequests.get(self.endpoint + 'Temperature').json()
        else:
            response = 99
        return(response)

    @property
    def pressure(self):
        '''
        Pressure in pascal.
        ''' 
        if self.endpoint != "":
            response = urequests.get(self.endpoint + 'Pressure').json()
        else:
            response = 1010 +  (4-random.getrandbits(3))
        return(response)
        
    @property
    def altitude(self):
        '''
        Altitude in m.
        '''
        try:
            p = -7990.0*math.log(self.pressure/self.baseline)
        except:
            p = 0.0
        return p
