"""
Collecting data from SCI well streams
"""
# standard
import os
# project
from clients.base import mqtt, parsers, writers


CV50_PS_MAPPING = ['w_pressure', 'w_temperature', 'w_level']
CSV_HEADER = (
    'label', 'received_utc', 'received_local', 'app_id', 'dev_id', 'prefix',
    'sensor_id', 'sub_sensor_id', 'nb_values', 'w_pressure',
    'w_temperature', 'w_level', 'battery_voltage', 'dev_rssi')
LABEL_MAPPING = {
    'tbs12s-fe5a03': 'SCI north well',
    'tbs12s-fe5a04': 'SCI south well',
    'tbs12s-029601': 'SCI cold spare'}
OUTPUT_TEMPLATE = os.path.join(os.path.expanduser("~"),
    'lora_data', os.path.splitext(os.path.split(__file__)[1])[0] + '.csv')


class TBS12SInSituParser(parsers.TBS12SParser):
    """
    A parser for the TBS12S/InSitu pressuere inducer setup
    """

    def get_sensor_data(self, dic):
        """
        Parses InSitu SDI 12 messages (preformatted by TBS12S)

        Args:
            dic(dict): A device data dictionary
        Returns:
            dict
        """
        ret = {}
        parts = dic.get('measurements', '').split(' ')
        for idx, itm in enumerate(CV50_PS_MAPPING):
            ret[itm] = float(parts[idx])
        return ret


class TBS12SinSituCSVWriter(writers.BaseCSVWriter):
    """
    A CSV writer for the TBS12S/CV50 setup
    """
    header = CSV_HEADER
    template = os.environ.get('DATA_FILE') or OUTPUT_TEMPLATE
    parser_class = TBS12SInSituParser
    # limit so that it can be opend in MS Excel
    max_lines = 60000
    print_message = False

    def additional_transformations(self, dic):
        """
        Lookup well names
        """
        dic['label'] = LABEL_MAPPING.get(dic.get('dev_id'))
        return dic

    def filter(self, dic):
        """
        Only store PS and PB messages
        """
        return dic.get('prefix') in ['PS', 'PB', 'C']


class TBS12SinSituClient(mqtt.BaseMQTTClient):
    """
    A client subscribing to the sci-chi-climate application
    (read uplinks)
    """
    host = 'nam1.cloud.thethings.industries'
    topic = 'v3/sci-wells@tnc/devices/+/up'
    username = 'sci-wells@tnc'


if __name__ == '__main__':
    writer = TBS12SinSituCSVWriter()
    TBS12SinSituClient(callback=writer.add_to_csv).run()
