'''
Mock Module for the MHZ19 pressure sensor.
Behaves like the MHZ19 library to be used as a drop in replacement
'''

import urequests
import time
import json

class mhz19:
    def __init__(self,  uart_no):
        self.ppm = 0
        self.temp = 0
        self.co2status = 0
        with open('config.json') as config_file:
            config = json.load(config_file)
        self.endpoint = f"{config['mock_endpoint']}{config['node_name']}/"

    def get_data(self):
        # leave in to ensure timining is similar to origianl Sensor
        time.sleep(0.1)

        if self.endpoint != "":
            self.ppm = urequests.get(self.endpoint + 'CO2').json()
            self.temp = urequests.get(self.endpoint + 'Temperature').json()
        else:
            self.ppm = 99
            self.temp = 99
        return(1)

