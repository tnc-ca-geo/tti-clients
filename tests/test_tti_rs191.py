"""
Test for Laird RS191 implementation
"""
# pylint:disable=C0103,C0115,C0116,R0903
# standard library
from unittest import TestCase
# project
from clients import tti_rs191


class Test_TTI_Parser(TestCase):

    def test_get_sensor_data(self):
        parser = tti_rs191.RS191_Parser()
        test_dic = {
            'rssi': -65, 'snr': 10.2, 'gw_id': 'lorix-one-20bb57', 'dr': 3,
            'payload': 'AWcAcAJorQMCASY=',
            'received_at': '2021-01-14T18:12:36.733218676Z',
            'dev_id': 'laird-rs191-00bfe1', 'app_id': 'laird-rs-191',
            'device': b'\x01g\x00p\x02h\xad\x03\x02\x01&'}
        self.assertEqual(parser.get_sensor_data(test_dic),{
            'temperature_sensor_1': 11.2, 'humidity_sensor_2': 86.5,
            'analog_input_3': 2.94})
