import time
import os
import json
# The Micropython Unix isn't including "/lib" in its path
import sys
sys.path.append('lib')

from lib.mqtt import MQTTClient

import sensors

def connect():
    connected = False
    if config['mqtt_user'] == "" or config['mqtt_password'] == "":
        client = MQTTClient(config['sensor_name'], config['mqtt_broker'], config['mqtt_port'],keepalive=30)
    else:
        client = MQTTClient(config['sensor_name'], config['mqtt_broker'], config['mqtt_port'], config['mqtt_user'], config['mqtt_password'],keepalive=30)
    while not connected:
        try:
            client.connect()
            connected = True
            print("Connected to MQTT Server")
        except OSError:
            print(f"Could not yet reach host {config['mqtt_broker']} on port {config['mqtt_port']}")
    return client

def measure(sensor_list):
    client = connect()
    while True:
        print("Sending measurements")
        for sensor in sensor_list:
            try:
                client.publish(config['mqtt_topic']+ "/" + sensor[0], str(sensor[1].read()))
            except OSError:
                print("Connection lost, try reconnect")
                client = connect()
        time.sleep(config['measure_interval'])


with open('config.json') as config_file:
    config = json.load(config_file)

try:
    if (os.uname()[0]=='esp32'):
        from machine import Pin
        physical = True
    else:
        physical = False
        #global endpoint
        #endpoint = f"{config['mock_endpoint']}/{config['sensor_name']}/" 
except AttributeError:
    physical = False
    time.sleep(30)
    physical = False
    #global endpoint
    #endpoint = f"{config['mock_endpoint']}/{config['sensor_name']}/"



sensor_list = []
sensor_list.append(['luminance',sensors.light_sensor(physical, scl=22, sda=21)])
sensor_list.append(['pressure',sensors.pressure_sensor(physical, scl=5, sda=4)])
sensor_list.append(['co2level',sensors.co2_sensor(physical, 2)])
sensor_list.append(['temperature', sensors.temperature_sensor(physical, config['temp_sensor_pin'])])
  
measure(sensor_list)
