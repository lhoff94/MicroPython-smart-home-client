import time

class sensor:

    def __init__(self):
        pass


    def read():
        pass


class light_sensor(sensor):

    def __init__(self, physical, scl, sda, addr=0x23):
        """
        Initializes a bh1750 pressure sensor
        :param scl: pin number of the serial clock line for the i2c interface
        :param sda: pin number of the serial data line for the i2c interface
        :param addr: i2c adreess, 0x23 is default, if addr pin is pulled high it is 0x5c
        """
        if physical:
            from machine import Pin, SoftI2C
            from bh1750 import BH1750
        else:
            from machine_mock import Pin, SoftI2C
            from bh1750_mock import BH1750            
        self.i2c = SoftI2C(scl=Pin(scl), sda=Pin(sda),)
        self.sensor = BH1750(self.i2c, addr)
        self.res = BH1750.ONCE_HIRES_1
    
    def read(self):
        return self.sensor.luminance(self.res)


class pressure_sensor(sensor):

    def __init__(self, physical, scl, sda):
        """
        Initializes a bmp180 pressure sensor
        :param scl: pin number of the serial clock line for the i2c interface
        :param sda: pin number of the serial data line for the i2c interface
        """
        super().__init__()
        if physical:
            from machine import Pin, SoftI2C
            from bmp180 import BMP180
        else:
            from machine_mock import Pin, SoftI2C
            from bmp180_mock import BMP180

        self.i2c = SoftI2C(scl=Pin(scl), sda=Pin(sda), freq=100000)
        self.sensor = BMP180(self.i2c)
        self.sensor.oversample_sett = 2

    def read(self, unit="hP"):
        if unit == "P":
            return self.sensor.pressure
        elif unit == "hP" or unit == "mbar":
            return self.sensor.pressure/100
        elif unit == "Bar":
            return self.sensor.pressure/100000
        else:
            raise ValueError("Unknown unit, use P, hP, mbar or Bar") 

    
    def read_temp(self):
        # The bmp180 has a additional temperature sensor, since its not the primary use
        # case its not exposed via the "read" function but a additional function
        """
        Measures Temperature and returns in celsius
        """
        return self.sensor.temperature

class co2_sensor(sensor):

    def __init__(self, physical, uart):
        if physical: 
            from mhz19 import mhz19
        else:
            from mhz19_mock import mhz19
        super().__init__()
        self.sensor = mhz19(uart)
    
    def read(self):
        self.sensor.get_data()
        return self.sensor.ppm
    
    def read_temp(self):
        # The mhz19 has a additional temperature sensor, since its not the primary use
        # case its not exposed via the "read" function but a additional function
        """
        Measures Temperature and returns in celsius
        """
        self.sensor.get_data()
        return self.sensor.temp

class temperature_sensor(sensor):

    def __init__(self, physical, pin):
        super().__init__()
        if physical:
            from machine import Pin
            from ds18x20 import DS18X20
            from onewire import OneWire
        else:
            from machine_mock import Pin
            from ds18x20_mock import DS18X20
            from onewire_mock import OneWire            
        self.sensor = DS18X20(OneWire(Pin(pin)))
        sensor_addrs = self.sensor.scan()
        if not sensor_addrs:
            raise Exception('no DS18B20 found at bus on pin %d' % pin)
        self.sensor_addr = sensor_addrs.pop()
    
    def read(self):
        self.sensor.convert_temp()
        time.sleep_ms(750)
        return self.sensor.read_temp(self.sensor_addr)

    






