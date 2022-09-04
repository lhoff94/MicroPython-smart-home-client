'''
Libarary that enables device discovery on Home Assistant.
Source: https://github.com/agners/micropython-ha-mqtt-device/blob/master/ha_mqtt_device.py
Commit: 8637c53d71adc62e267a5f6bd0a10060c1c8460c
License: 
MIT License
Copyright (c) 2020 Stefan Agner
Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:
The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

import ujson as json

class BaseEntity(object):

    def __init__(self, mqtt, name, component, object_id, node_id, discovery_prefix, extra_conf):
        self.mqtt = mqtt

        base_topic = discovery_prefix + b'/' + component + b'/'
        if node_id:
            base_topic += node_id + b'/'
        base_topic += object_id + b'/'

        self.config_topic = base_topic + b'config'
        self.state_topic = base_topic + b'state'

        self.config = {"name": name, "state_topic": self.state_topic}
        if extra_conf:
            self.config.update(extra_conf)
        self.mqtt.publish(self.config_topic, bytes(json.dumps(self.config), 'utf-8'), True, 1)

    def remove_entity(self):
        self.mqtt.publish(self.config_topic, b'', 1)

    def publish_state(self, state):
        self.mqtt.publish(self.state_topic, state)

class BinarySensor(BaseEntity):

    def __init__(self, mqtt, name, object_id, node_id=None,
            discovery_prefix=b'homeassistant', extra_conf=None):

        super().__init__(mqtt, name, b'binary_sensor', object_id, node_id,
                discovery_prefix, extra_conf)

    def publish_state(self, state):
        self.mqtt.publish(self.state_topic, b'ON' if state else b'OFF')
            
    def on(self):
        self.publish_state(True)

    def off(self):
        self.publish_state(False)

class Sensor(BaseEntity):

    def __init__(self, mqtt, name, object_id, node_id=None,
            discovery_prefix=b'homeassistant', extra_conf=None):

        super().__init__(mqtt, name, b'sensor', object_id, node_id,
                discovery_prefix, extra_conf)

class EntityGroup(object):

    def __init__(self, mqtt, node_id, discovery_prefix=b'homeassistant',
            extra_conf={}):
        self.mqtt = mqtt
        self.node_id = node_id
        self.discovery_prefix = discovery_prefix
        # Group wide extra conf, gets passed to sensors
        self.extra_conf = extra_conf
        # Read state_topic from config if provided
        if "state_topic" in extra_conf:
            self.state_topic = extra_conf["state_topic"]
        else:
            self.state_topic = discovery_prefix + b'/sensor/' + node_id + b'/state'
            extra_conf["state_topic"] = self.state_topic
        self.entities = []

    def _update_extra_conf(self, extra_conf):
        if "value_template" not in extra_conf:
            raise Exception("Groupped sensors need value_template to be set.")
        extra_conf.update(self.extra_conf)

    def create_binary_sensor(self, name, object_id, extra_conf):
        self._update_extra_conf(extra_conf)
        bs = BinarySensor(self.mqtt, name, object_id, self.node_id,
                self.discovery_prefix, extra_conf)
        self.entities.append(bs)
        return bs

    def create_sensor(self, name, object_id, extra_conf):
        self._update_extra_conf(extra_conf)
        s = Sensor(self.mqtt, name, object_id, self.node_id,
                self.discovery_prefix, extra_conf)
        self.entities.append(s)
        return s

    def publish_state(self, state):
        self.mqtt.publish(self.state_topic, bytes(json.dumps(state), 'utf-8'))

    def remove_group(self):
        for e in self.entities:
            e.remove_entity()


