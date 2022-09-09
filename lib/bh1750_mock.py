"""
Micropython BH1750 ambient light sensor driver.
"""

import urequests
import json
import random


class BH1750():
    """
    Micropython BH1750 ambient light sensor driver Mock.
    Behaves like the BH1750 library to be used as a drop in replacement
    """
    CONT_LOWRES = 0x13
    CONT_HIRES_1 = 0x10
    CONT_HIRES_2 = 0x11
    ONCE_HIRES_1 = 0x20
    ONCE_HIRES_2 = 0x21
    ONCE_LOWRES = 0x23
    def __init__(self, bus, addr=0x23):
        with open('config.json') as config_file:
            config = json.load(config_file)
        if config['mock_endpoint'] != "":
            self.endpoint = f"{config['mock_endpoint']}{config['node_name']}/"
        else:
            self.endpoint = "" 
        pass

    def luminance(self, mode):
        """Sample luminance (in lux), using specified sensor mode."""
        if self.endpoint != "":
            response = urequests.get(self.endpoint + 'Luminance').json()
        else:
            response = 50 +  random.randint(0, 10)
        return(response)