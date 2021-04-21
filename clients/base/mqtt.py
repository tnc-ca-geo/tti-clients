# pylint:disable=C0103,W0613,E0401
"""
A base client for TTI interaction via MQTT (subscribe)
"""
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
        """
        Connect to MQTT by inializing the class.

        Args:
            password(str): MQTT password, optional can be taken from ENV
            callbace(func): A callback function .on_message
            connect_callback(func): A callback function for .on_connect
        """
        self.process_callback = callback or self.noop
        self.connect_callback = connect_callback or self.noop
        password = password or os.environ.get(self.pw_env_var)
        self.client = self.connect(password=password)

    def connect(self, password):
        """
        Establish connection and return client object.

        Args:
            password(str): MQTT password

        Returns:
            Instance of mqtt.Client
        """
        client = mqtt.Client()
        client.on_connect = self.on_connect
        client.on_message = self.on_message
        client.on_disconnect = self.on_disconnect
        client.username_pw_set(self.username, password=password)
        client.connect(self.host, 1883, 10)
        client.subscribe(self.topic)
        return client

    def noop(self, *args, **kwargs):
        """
        An empty function as a placeholder
        """

    def run(self):
        """
        Start the polling loop
        """
        self.client.loop_forever()

    def on_message(self, client, data, msg):
        """
        Wrap the message callback function, the footprint is determined
        by the paho.mqtt package
        """
        print('message received from', self.topic)
        self.process_callback(msg)

    def on_connect(self, client, data, flags, rc):
        """
        Wrap the connect callback function, the footprint is determined
        by the paho.mqtt package
        """
        print('MQTT response code: {}, {}'.format(rc, MQTT_RCS[rc]))
        self.connect_callback()

    def on_disconnect(self, client, data, rc):
        print('Connection lost, MQTT response code: {}, {}'.format(
            rc, MQTT_RCS[rc]))
