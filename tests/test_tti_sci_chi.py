# standard library
from unittest import TestCase, mock
import os
import shutil
from types import SimpleNamespace
# project
from clients.base import parsers, writers
from clients import tti_sci_chi
# tests
from tests.shared import PayloadTestCase, TEST_DIRECTORY


class TestTBS12SCV50Parser(PayloadTestCase):

    def test_get_sensor_data(self):
        test_data = {
            'measurements': (
            '+78.0 +0.0 +0.0 +0.0 +0.62 +321.5 +1.95 +13.8 +1.27 '
            '+101.89 +0.807 +13.7 +3.0 +2.9 +0.0 +0.49 -0.39 +1.95')}
        parser = tti_sci_chi.TBS12S_CV50_Parser()
        res = parser.get_sensor_data(test_data)
        self.assertEqual(res, {
            'solar_flux_density': 78.0, 'precipitation': 0.0, 
            'lightening_strike_count': 0.0, 'strike_distance': 0.0, 
            'wind_speed': 0.62, 'wind_direction': 321.5, 'max_wind_speed': 1.95, 
            'air_temp': 13.8, 'vapor_pressure': 1.27, 'barometric_pressure': 101.89, 
            'rel_humidity': 0.807, 'humidity_sensor_temp': 13.7, 
            'tilt_north_south': 3.0, 'tilt_west_east': 2.9, 'compass_heading': 0.0, 
            'north_wind_speed': 0.49, 'east_wind_speed': -0.39, 
            'wind_speed_max': 1.95})


class TestTBS12SCV50CSVWriter(PayloadTestCase):

    # This tests a somewhat convoluted setup and is here to 
    # ensure prior behavior.
    # TODO: replace with tests more focussed on actual units
    def test_parse(self):
        writer = tti_sci_chi.TBS12S_CV50_CSV_Writer()
        msg = SimpleNamespace(payload=self.example_message.payload)
        self.assertEqual(writer.serialize(msg), (
            '2021-01-04T23:46:05.124510287Z,2000-01-01 02:30:00,'
            'sci-chi-climate,tbs-12s-aa0120,PS,0,0,18,78.0,0.0,0.0,'
            '0.0,0.62,321.5,1.95,13.8,1.27,101.89,0.807,13.7,3.0,2.9,'
            '0.0,0.49,-0.39,1.95,,-51,,10,3,laird-rg191-296af5'))
