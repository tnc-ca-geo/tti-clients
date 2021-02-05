"""
Listen to the tektelic asset-tracker application,
and send coordinates to Arcgis Online
"""
from clients.base import mqtt, parsers, writers


class Tektelic_AGO_Writer(writers.BaseAGOWriter):
    parser_class = parsers.TektelicTrackerParser


class Tektelic_Client(mqtt.BaseMQTTClient):
    host = 'nam1.cloud.thethings.industries'
    topic = 'v3/tektelic-asset-trackers@tnc/devices/+/up'
    username = 'tektelic-asset-trackers@tnc'

    # for debugging
    # def process_callback(msg):
    #       print(msg)


if __name__ == "__main__":
    writer = Tektelic_AGO_Writer()
    Tektelic_Client(callback=writer.add_to_ago).run()
