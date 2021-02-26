# pylint:disable=R0201,W0613
"""
Base classes to parse LoRaWAN data

The TBS12S device did get a base class because of common
use at TNC
"""
# standard library
import base64
from datetime import datetime
import json
import pytz
import re


TBS12S_MESSAGE_PATTERN = re.compile(
    r'^(?P<prefix>[A-Z]+)(?P<time>\d{2}:\d{2}:\d{2}:\d{2}:\d{2}:00)'
    r'(?P<data>[RS0-9]*)[ ]*(?P<measurements>.*)$')


class BaseParser():
    """
    A base class parsing MQTT messages from TTI. Subclass and re-implement
    .get_device_data and .get_sensor_data to customize for a particular
    device/sensor setup.
    """

    def bytes_to_dict(self, byte_string):
        """
        Convert a byte payload to a dictionary

        Args:
            byte_string(bytes): A byte string containing utf-8 encode JSON
        Returns:
            dict
        """
        return json.loads(byte_string.decode('utf-8'))

    def get_payload(self, dic):
        """
        Extract and decode LoRaWAN payload field.

        Args:
            dic(dict): A dictionary containing LoRaWAN data
        Returns:
            bytes
        """
        return base64.b64decode(
            dic.get('uplink_message', {}).get('frm_payload', b''))

    def parse(self, msg):
        """
        Parse the message in three steps:

        1. LoRaWAN payload which wrapes
        2. Device payload which contains
        3. Sensor data

        Args:
            msg(paho.mqtt message object): The message
        Returns:
            dict
        """
        ret = {}
        dic = self.bytes_to_dict(msg.payload)
        ret.update(self.get_lorawan_metadata(dic))
        payload = self.get_payload(dic)
        ret.update(self.get_device_data(payload))
        if self.sensor_condition(ret):
            ret.update(self.get_sensor_data(ret))
        return ret

    def get_lorawan_metadata(self, dic):
        """
        Parse out the metadata from LoRaWAN network server

        Args:
            dic(dict): Message in dict format
        Returns:
            dict
        """
        uplink_message = dic.get('uplink_message', {})
        rx_metadata = uplink_message.get('rx_metadata')
        ret = {}
        for item in rx_metadata or []:
            rssi = item.get('rssi', -999)
            if rssi > ret.get('rssi', -999):
                ret['rssi'] = rssi
                ret['snr'] = item.get('snr')
                ret['gw_id'] = item.get('gateway_ids', {}).get('gateway_id')
        ret['dr'] = uplink_message.get('settings', {}).get('data_rate_index')
        ret['payload'] = uplink_message.get('frm_payload')
        ret['received_at'] = uplink_message.get('received_at')
        end_device_ids = dic.get('end_device_ids', {})
        ret['dev_id'] = end_device_ids.get('device_id')
        ret['app_id'] = end_device_ids.get(
            'application_ids', {}).get('application_id')
        return ret

    def get_device_data(self, byte_string):
        """
        Parse device data (placeholder)

        Args:
            byte_string(bytes): The decoded message.
        Returns:
            dict
        """
        return {'device': byte_string}

    def sensor_condition(self, dic):
        """
        A condition under which sensor data will be processed

        Args:
            dic(dict): Data dictionary.
        Returns:
            boolean
        """
        return True

    def get_sensor_data(self, dic):
        """
        Parse out sensor data

        Args:
            dic(dict)
        Returns:
            dic
        """
        return {}


class TBS12SParser(BaseParser):
    """
    A parser for TBS12S devices
    """

    def get_device_data(self, byte_string):
        """
        Parse out TBS12S data

        Args:
            byte_string(bytes)
        Returns:
            dict
        """
        res = TBS12S_MESSAGE_PATTERN.match(byte_string.decode('utf-8'))
        if not res:
            return {}
        ret = {
            'prefix': res['prefix'],
            'device_time': datetime.strftime(
                datetime.strptime(res['time'],
            '%y:%m:%d:%H:%M:%S'), '%Y-%m-%d %H:%M:%S'),
            'measurements': res['measurements']}
        if ret.get('prefix') == 'PS':
            ret['sensor_id'] = res['data'][0]
            ret['sub_sensor_id'] = res['data'][1]
            ret['nb_values'] = int(res['data'][2:4])
        if ret.get('prefix') == 'C':
            ret['board_id'] = res['data'][0:8]
            ret['fw_version'] = res['data'][8:16]
            ret['power_supply'] = res['data'][16]
            ret['sensor_nb'] = int(res['data'][17])
            ret['status'] = res['data'][18]
            ret['dev_rssi'] = int(res['measurements'])
        if ret.get('prefix') == 'PB':
            ret['battery_voltage'] = float(res['measurements'])
        return ret

    def sensor_condition(self, dic):
        """
        Process sensor data when prefix field equals 'PS'

        Args:
            dic(dict)
        Returns:
            dict
        """
        return dic.get('prefix') == 'PS'


class TektelicTrackerParser(BaseParser):

    def convert_bytestring_to_hexrepresentation(self, bytes_string):
        """
        This might be helpful for debugging (unused for the actual parsing)
        """
        ret = ''
        for item in list(bytes_string):
            hx = hex(item)[2:]
            ret += (hx if len(hx) == 2 else "0" + hx) + ' '
        return ret[:-1]

    def get_device_data(self, byte_string):
        return {'device': self.convert_bytestring_to_hexrepresentation(
            byte_string)}


class FeatherTrackerParser(BaseParser):

    def get_time(self, received):
        utc = pytz.timezone('UTC')
        pst = pytz.timezone('America/Los_Angeles')
        try:
            received = received.split('.')[0]
            rec_time = datetime.strptime(received, '%Y-%m-%dT%H:%M:%S')
            rec_time = utc.localize(rec_time)
            return rec_time.astimezone(pst).strftime('%Y-%m-%d %H:%M:%S')
        except (AttributeError, ValueError):
            return None

    def parse(self, msg):
        """
        Since we have very different devices in this application, we rely
        on payload formatters.
        """
        dic = self.bytes_to_dict(msg.payload)
        payload = dic.get('uplink_message', {}).get('decoded_payload', {})
        ret = self.get_lorawan_metadata(dic)
        ret.update({
            'time': self.get_time(payload.get('time')) or self.get_time(
                dic.get('received_at')),
            'lon': payload.get('longitudeDeg', 0),
            'lat': payload.get('latitudeDeg', 0),
            'valid_fix': not payload.get(payload.get('fixFailed'))})
        if ret['lon'] == 1000 or ret['lat'] == 1000:
            ret['valid_fix'] = False
        return ret
