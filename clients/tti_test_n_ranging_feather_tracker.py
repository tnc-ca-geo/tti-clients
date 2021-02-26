"""
A client sending data from trackers to AGO
"""
from clients.base import mqtt, parsers, writers


class TrackerAGOWriter(writers.BaseAGOWriter):
    parser_class = parsers.FeatherTrackerParser


class TrackerClient(mqtt.BaseMQTTClient):
    host = 'nam1.cloud.thethings.industries'
    topic = 'v3/test-n-ranging@tnc/devices/+/up'
    username = 'test-n-ranging@tnc'


if __name__ == '__main__':
    writer = TrackerAGOWriter()
    TrackerClient(callback=writer.add_to_ago).run()
