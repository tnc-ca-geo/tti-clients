# pylint:disable=C0115,C0116
"""
Test base writer classes
"""
# standard library
import os
from unittest import mock
# project
from clients.base import writers
# tests
from tests.shared import PayloadTestCase, TEST_DIRECTORY


@mock.patch('clients.base.writers.BaseCSVWriter.template',
    new=os.path.join(TEST_DIRECTORY, 'test.csv'))
class TestBaseCSVWriter(PayloadTestCase):

    @mock.patch('clients.base.writers.BaseCSVWriter.header',
        new = ['activity', 'sport', 'animal'])
    def test_create_csv_line(self):
        test_dic = {
            'animal': 'cat', 'food': 'milk', 'activity': 'fun'}
        writer = writers.BaseCSVWriter()
        self.assertEqual(writer.create_csv_line(test_dic), 'fun,,cat')

    @mock.patch('clients.base.writers.BaseCSVWriter.header',
        new = ['rssi', 'dev_id', 'app_id'])
    def test_add_to_csv_creation(self):
        writer = writers.BaseCSVWriter()
        writer.add_to_csv(self.example_message)
        with open(writer.get_path()) as filehandle:
            self.assertEqual(filehandle.read(),
                'rssi,dev_id,app_id\n-51,tbs-12s-aa0120,sci-chi-climate\n')

    @mock.patch('clients.base.writers.BaseCSVWriter.header',
        new = ['rssi', 'missing', 'dev_id', 'app_id'])
    def test_add_to_csv_append(self):
        writer = writers.BaseCSVWriter()
        for _ in [0, 1]:
            writer.add_to_csv(self.example_message)
        with open(writer.get_path()) as filehandle:
            self.assertEqual(filehandle.read(),
                'rssi,missing,dev_id,app_id\n'
                '-51,,tbs-12s-aa0120,sci-chi-climate\n'
                '-51,,tbs-12s-aa0120,sci-chi-climate\n')
