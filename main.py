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

# Method to initialized the MQTT connection
def connect():
    connected = False
    if config['mqtt_user'] == "" or config['mqtt_password'] == "":
        client = MQTTClient(config['node_name'], config['mqtt_broker'], config['mqtt_port'],keepalive=35)
    else:
        client = MQTTClient(config['node_name'], config['mqtt_broker'], config['mqtt_port'], config['mqtt_user'], config['mqtt_password'],keepalive=30)
    while not connected:
        try:
            client.connect()
            connected = True
            print("Connected to MQTT Server")
        except OSError:
            print(f"Could not yet reach host {config['mqtt_broker']} on port {config['mqtt_port']}")
    return client

# Method to initialized ha device discovery and announce device and sensors
def setup_device_discovery(client, sensor_list):
    device_conf = { 
        "identifiers": config['node_name'], 
        "name": config['node_name'],
        "manufacturer": config['manufacturer'],
        "model": config['model'],
        "sw_version": config['sw_version'] }
    common_conf = { "device": device_conf }
    group = EntityGroup(client, bytes(config["node_name"],'ascii'), extra_conf=common_conf)
    for sensor in sensor_list:
        extra_config = { 
            "unit_of_measurement": sensor.get_unit(), 
            "device_class": sensor.get_device_class(),
            "value_template": sensor.get_value_template(),
            "unique_id": config['node_name'] + "-" + sensor.get_name() }
        group.create_sensor(bytes(sensor.get_name(),'ascii'), bytes(sensor.get_name(),'ascii'), extra_conf=extra_config)
    return group
    
# This Method parses the sensorlist form config and initializes sensors
def setup_sensor(sensor_info, physical):
    id = sensor_info.get("id")
    type = sensor_info.get("sensor_type")
    pins = sensor_info.get("pins")
    if type == "light_sensor":
        sensor_obj = sensors.light_sensor(physical, pins, id)
    elif type == "pressure_sensor":
        sensor_obj = sensors.pressure_sensor(physical, pins, id)
    elif type == "co2_sensor":
        sensor_obj = sensors.co2_sensor(physical, pins, id)
    elif type == "temperature_sensor":
        sensor_obj = sensors.temperature_sensor(physical, pins, id)
    return sensor_obj


# Method to continiously measure and publish the results
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

# Depending on the environment the software detects if its in a emulated environment or not
try:
    # Test if Board is esp32, curently only this type is supported
    if (os.uname()[0]=='esp32'):
        from machine import Pin
        physical = True
    else:
        physical = False
except AttributeError:
    physical = False
    time.sleep(30)
    physical = False

# Initializing sensor list
sensor_list = []
for sensor in config["sensors"]:
    sensor_list.append(setup_sensor(sensor,physical))

# start measuring
measure(sensor_list)
