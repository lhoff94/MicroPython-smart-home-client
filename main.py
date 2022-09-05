import time
import os
import json

import setup



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
    sensor_list.append(setup.setup_sensor(sensor,physical))

# Initializing MQTT connection
client = setup.setup_connection(config)

# Initializing HA decive discovery
group = setup.setup_device_discovery(config,client, sensor_list)


# start measuring
results = {}
while True:
    print("Sending measurements")
    for sensor in sensor_list:
        results[sensor.get_device_class()] = sensor.read()
    try:
        group.publish_state(results)
    except OSError:
        # reconnect if connection get lost
        print("Connection lost, try reconnect")
        client = setup.setup_connection()
    time.sleep(config['measure_interval'])
