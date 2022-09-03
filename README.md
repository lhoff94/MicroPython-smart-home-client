# MicroPython Smart Home Client

This repository contains code to use a ESP32 DevBoard as a sensor node. 
It supports drivers for the following sensors:
- BH17500
- BMP180
- MH-Z19c
- DS18x20

The results can be send via MQTT. 
All necessary configurations are imported from a config.json. 

Additonally the repository contains mock drivers to test the code without the sensors attached (e.g. in within a Docker container [1])

Tested with MicroPython v1.18

[1] See here for a compatible Docker image:  https://hub.docker.com/r/lhoff94/micropython-runtime

## Flashing 

To flash the code to a compatible 
