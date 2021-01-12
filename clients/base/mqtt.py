# standard library
import os
# third party
import paho.mqtt.client as mqtt


MQTT_RCS = [
    'Connection accepted',
    'Connection refused, unacceptable protocol version',
    'Connection refused, identifier rejected',
    'Connection refused, server unavailable',
    'Connection refused, bad user name or password',
    'Connection refused, not authorized']


class BaseMQTTClient():
    """
    A generic class to parse MQTT coming from TTI
    """
    host = '' 
    topic = ''
    username = ''
    pw_env_var = 'MQTT_PW'

    def __init__(
            self, password=None, callback=None, connect_callback=None
    ):
        self.process_callback = callback or self.noop
        self.connect_callback = connect_callback or self.noop
        password = password or os.environ.get(self.pw_env_var) 
        self.client = self.connect(password=password)

    def connect(self, password):
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.username_pw_set(self.username, password=password)
        client.connect(self.host, 1883, 60)
        client.subscribe(self.topic)
        return client

    def noop(self, *args, **kwargs):
        pass

    def run(self):
        self.client.loop_forever()
    
    def on_message(self, client, data, msg):
        print('message received from', self.topic)
        self.process_callback(msg)

    def on_connect(self, client, data, flags, rc):
        print('MQTT response code: {}, {}'.format(rc, MQTT_RCS[rc]))
        self.connect_callback()
