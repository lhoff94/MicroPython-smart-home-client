import random
import urequests
import json


class DS18X20:
    def __init__(self, onewire):
        self.onewire = onewire
        with open('config.json') as config_file:
            config = json.load(config_file)
        if config['mock_endpoint'] != "":
            self.endpoint = f"{config['mock_endpoint']}{config['node_name']}/"
        else:
            self.endpoint = "" 
        return None

    def scan(self):
        # Returns False so that probe if sensor was found still passes
        return [True]

    def convert_temp(self):
        return 1

    def read_temp(self, rom):
        '''
        Temperature in degree C.
        '''
        if self.endpoint != "":
            response = urequests.get(self.endpoint + 'Temperature').json()
        else:
            response = 50 + random.randint(0, 10)
        return(response)

