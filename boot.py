# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#import webrepl
#webrepl.start()
import json

with open('config.json') as config_file:
    config = json.load(config_file)


def do_connect():
    import network
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('connecting to network...')
        wlan.connect(config['wifi_ssid'], config['wifi_password'],)
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())
    
do_connect()