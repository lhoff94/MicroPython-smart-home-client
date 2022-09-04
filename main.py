import time
import os
import json
# The Micropython Unix isn't including "/lib" in its path
import sys
sys.path.append('lib')

from lib.ha_mqtt import Sensor,EntityGroup
from lib.umqtt import MQTTClient
#from lib.mqtt import MQTTClient

import sensors

def connect():
    connected = False
    if config['mqtt_user'] == "" or config['mqtt_password'] == "":
        client = MQTTClient(config['sensor_name'], config['mqtt_broker'], config['mqtt_port'],keepalive=35)
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

def setup_device_discovery(client, sensor_list):
    device_conf = { 
        "identifiers": config['sensor_name'], 
        "name": config['sensor_name'],
        "manufacturer": config['manufacturer'],
        "model": config['model'],
        "sw_version": config['sw_version'] }
    common_conf = { "device": device_conf }
    group = EntityGroup(client, bytes(config["sensor_name"],'ascii'), extra_conf=common_conf)
    for sensor in sensor_list:
        extra_config = { 
            "unit_of_measurement": sensor.get_unit(), 
            "device_class": sensor.get_device_class(),
            "value_template": sensor.get_value_template(),
            "unique_id": config['sensor_name'] + "-" + sensor.get_name() }
        group.create_sensor(bytes(sensor.get_name(),'ascii'), bytes(sensor.get_name(),'ascii'), extra_conf=extra_config)
    return group
    


def measure(sensor_list):
    client = connect()
    group = setup_device_discovery(client, sensor_list)
    results = {}
    while True:
        print("Sending measurements")
        for sensor in sensor_list:
            results[sensor.get_device_class()] = sensor.read()
        try:
            group.publish_state(results)
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
sensor_list.append(sensors.light_sensor(physical, scl=22, sda=21))
sensor_list.append(sensors.pressure_sensor(physical, scl=5, sda=4))
sensor_list.append(sensors.co2_sensor(physical, 2))
sensor_list.append(sensors.temperature_sensor(physical, 25))

measure(sensor_list)
