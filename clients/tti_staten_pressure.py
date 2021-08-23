# pylint:disable=C0103
"""
Listen to the staten-island-sensors@tnc application
"""

# standard library
from base64 import b64decode
import os
# third party
from cayennelpp import LppFrame, lpp_type
# project
from clients.base import mqtt, parsers, writers


# order of fields is compatible with older TTN application
CSV_HEADER = (
    'received_at','received_local','dev_id','Analog_Input_1','Barometer_2',
    'Analog_Input_3','rssi','Analog_Input_4')
OUTPUT_TEMPLATE = os.path.join(os.path.expanduser("~"),
    'lora_data', os.path.splitext(os.path.split(__file__)[1])[0] + '.csv')


class Analog_Pressure_Parser(parsers.BaseParser):
    """
    A parser for the TBS12S/CV50 setup (micro weather station)
    """

    def get_sensor_data(self, dic):
        """
        Parses RS191 Cayenne messages (preformatted by TBS12S)

        Args:
            dic(dict): A device data dictionary
        Returns:
            dict
        """
        ret = {}
        frame = LppFrame()
        decoded = frame.from_bytes(b64decode(dic.get('payload')))
        for item in decoded:
            type_name = item.type.name
            field_name = '_'.join(
                type_name.split(' ') + [str(item.channel)])
            # use single value for now until we encounter tuples with more
            # than one value
            value = item.value[0]
            ret.update({field_name: value})
        return ret


class Analog_Pressure_CSV_Writer(writers.BaseCSVWriter):
    """
    A CSV writer for the TBS12S/CV50 setup
    """
    header = CSV_HEADER
    template = os.environ.get('DATA_FILE') or OUTPUT_TEMPLATE
    parser_class = Analog_Pressure_Parser
    # limit so that it can be opend in MS Excel
    max_lines = 60000


class Analog_Pressure_Client(mqtt.BaseMQTTClient):
    """
    A client subscribing to the sci-chi-climate application
    (read uplinks)
    """
    host = 'nam1.cloud.thethings.industries'
    topic = 'v3/staten-island-sensors@tnc/devices/+/up'
    username = 'staten-island-sensors@tnc'


if __name__ == '__main__':
    writer = Analog_Pressure_CSV_Writer()
    Analog_Pressure_Client(callback=writer.add_to_csv).run()
