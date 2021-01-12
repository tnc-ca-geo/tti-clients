# project
from clients.base import parsers
# tests
from tests.shared import PayloadTestCase


class TestBaseParser(PayloadTestCase):

    def test_bytes_to_dict(self):
        parser = parsers.BaseParser()
        res = parser.bytes_to_dict(self.example_message.payload)
        self.assertIn('received_at', res)
        self.assertIsInstance(res, dict)

    def test_get_lorawan_metadata(self):
        parser = parsers.BaseParser()
        dic = parser.bytes_to_dict(self.example_message.payload)
        res = parser.get_lorawan_metadata(dic)
        self.assertEqual(res, {
            'rssi': -51, 'snr': 10, 'gw_id': 'laird-rg191-296af5', 'dr': 3, 
            'payload': (
                'UFMwMDowMTowMTowMjozMDowMDAwMTggKzc4LjAgKzAuMCArMC4wICswLj'
                'AgKzAuNjIgKzMyMS41ICsxLjk1ICsxMy44ICsxLjI3ICsxMDEuODkgKzAu'
                'ODA3ICsxMy43ICszLjAgKzIuOSArMC4wICswLjQ5IC0wLjM5ICsxLjk1'), 
            'received_at': '2021-01-04T23:46:05.124510287Z', 
            'dev_id': 'tbs-12s-aa0120', 'app_id': 'sci-chi-climate'})


class TestTBS12SParser(PayloadTestCase):

    def test_get_device_data(self):
        parser = parsers.TBS12SParser()
        ps_message =  (
            b'PS00:01:01:02:30:000018 +78.0 +0.0 +0.0 +0.0 +0.62 +321.5'
            b' +1.95 +13.8 +1.27 +101.89 +0.807 +13.7 +3.0 +2.9 +0.0 +0.49'
            b' -0.39 +1.95')
        self.assertEqual(parser.get_device_data(ps_message), {
            'prefix': 'PS', 'device_time': '2000-01-01 02:30:00', 
            'measurements': (
                '+78.0 +0.0 +0.0 +0.0 +0.62 +321.5 +1.95 +13.8 +1.27 '
                '+101.89 +0.807 +13.7 +3.0 +2.9 +0.0 +0.49 -0.39 +1.95'), 
            'sensor_id': '0', 'sub_sensor_id': '0', 'nb_values': 18}) 
            # 'solar_flux_density': 78.0, 'precipitation': 0.0, 
            # 'lightening_strike_count': 0.0, 'strike_distance': 0.0, 
            # 'wind_speed': 0.62, 'wind_direction': 321.5, 'max_wind_speed': 1.95, 
            # 'air_temp': 13.8, 'vapor_pressure': 1.27, 'barometric_pressure': 101.89, 
            # 'rel_humidity': 0.807, 'humidity_sensor_temp': 13.7, 
            # 'tilt_north_south': 3.0, 'tilt_west_east': 2.9, 'compass_heading': 0.0, 
            # 'north_wind_speed': 0.49, 'east_wind_speed': -0.39, 'wind_speed_max': 1.95})
        c_message = b'C00:01:01:04:39:00544253530200010701R -105'
        self.assertEqual(parser.get_device_data(c_message), {
            'prefix': 'C', 'device_time': '2000-01-01 04:39:00', 'board_id': '54425353', 
            'fw_version': '02000107', 'power_supply': '0', 'sensor_nb': 1, 
            'status': 'R', 'measurements': '-105', 'dev_rssi': -105})
        pb_message = b'PB00:01:01:02:30:00 2.66'
        self.assertEqual(parser.get_device_data(pb_message), {
            'prefix': 'PB', 'device_time': '2000-01-01 02:30:00', 'measurements': '2.66',
            'battery_voltage': 2.66})
        self.assertEqual(parser.get_device_data(b''), {})



