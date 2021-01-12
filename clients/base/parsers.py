#standard library
import base64
from datetime import datetime
import json
import re


TBS12S_MESSAGE_PATTERN = re.compile(
    r'^(?P<prefix>[A-Z]+)(?P<time>\d{2}:\d{2}:\d{2}:\d{2}:\d{2}:00)'
    r'(?P<data>[RS0-9]*)[ ]*(?P<measurements>.*)$')


class BaseParser():
    """
    A base class parsing MQTT messages from TTI. Subclass and
    re-implement .get_device_data and .get_sensor_data to customize
    for a particular device/sensor setup.
    """

    def bytes_to_dict(self, byte_string):
        return json.loads(byte_string.decode('utf-8'))

    def get_payload(self, dic):
        return base64.b64decode(
            dic.get('uplink_message', {}).get('frm_payload', b''))

    def parse(self, msg):
        ret = {}
        dic = self.bytes_to_dict(msg.payload)
        ret.update(self.get_lorawan_metadata(dic))
        payload = self.get_payload(dic)
        ret.update(self.get_device_data(payload))
        if self.sensor_condition(ret):
            ret.update(self.get_sensor_data(ret))
        return ret

    def get_lorawan_metadata(self, dic):
        uplink_message = dic.get('uplink_message', {})
        rx_metadata = uplink_message.get('rx_metadata')
        ret = {}
        for item in rx_metadata:
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
        return {'device': byte_string}

    def sensor_condition(self, dic):
        return True

    def get_sensor_data(self, dic):
        return {}


class TBS12SParser(BaseParser):

    def get_device_data(self, byte_string):
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
            # ret.update(sensor_function(res['measurements']))
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
        return dic.get('prefix') == 'PS'
