"""
Listen to sci-sci-climate and logs data into CSV
"""
# standard
import base64
import codecs
from datetime import datetime
import json
import os
import re
# third party
# project
from clients.base import mqtt, parsers, writers


CV50_PS_MAPPING = [
    'solar_flux_density', 'precipitation', 'lightening_strike_count',
    'strike_distance', 'wind_speed', 'wind_direction', 'max_wind_speed',
    'air_temp', 'vapor_pressure', 'barometric_pressure', 'rel_humidity',
    'humidity_sensor_temp', 'tilt_north_south', 'tilt_west_east',
    'compass_heading', 'north_wind_speed', 'east_wind_speed', 
    'wind_speed_max']
CSV_HEADER = (
    'received_at', 'device_time', 'app_id', 'dev_id', 'prefix',
    'sensor_id', 'sub_sensor_id', 'nb_values', 'solar_flux_density', 
    'precipitation', 'lightening_strike_count', 'strike_distance', 
    'wind_speed', 'wind_direction', 'max_wind_speed', 'air_temp', 
    'vapor_pressure', 'barometric_pressure', 'rel_humidity', 
    'humidity_sensor_temp', 'tilt_north_south', 'tilt_west_east', 
    'compass_heading', 'north_wind_speed', 'east_wind_speed', 
    'wind_speed_max', 'battery_voltage', 'rssi', 'dev_rssi', 'snr',
    'dr', 'gw_id')
OUTPUT_TEMPLATE = os.path.join(os.path.expanduser("~"), 
    'lora_data', os.path.splitext(os.path.split(__file__)[1])[0] + '.csv') 


class TBS12S_CV50_Parser(parsers.TBS12SParser):

    def get_sensor_data(self, dic):
        ret = {}
        parts = dic.get('measurements', '').split(' ')
        for idx, itm in enumerate(CV50_PS_MAPPING):
            ret[itm] = float(parts[idx])
        return ret


class TBS12S_CV50_CSV_Writer(writers.BaseCSVWriter):
    header = CSV_HEADER
    template = OUTPUT_TEMPLATE
    parser_class = TBS12S_CV50_Parser


class TBS12S_CV50_Client(mqtt.BaseMQTTClient):
    host = 'nam1.cloud.thethings.industries'
    topic = 'v3/sci-chi-climate@tnc/devices/+/up'
    username = 'sci-chi-climate@tnc' 


if __name__ == '__main__':
    parser = TBS12S_CV50_CSV_Writer() 
    TBS12S_CV50_Client(callback=parser.add_to_csv).run()
