# pylint:disable=C0115,C0116
"""
Test base writer classes
"""
# standard library
from datetime import datetime
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
        self.assertEqual(writer.create_csv_line(test_dic), 'fun,,cat\n')

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

    @mock.patch.multiple('clients.base.writers.BaseCSVWriter',
        header=['rssi', 'missing', 'dev_id', 'app_id'], max_lines=20)
    def test_max_lines(self):
        writer = writers.BaseCSVWriter()
        for _ in range(0, 100):
            writer.add_to_csv(self.example_message)
        res = os.listdir(TEST_DIRECTORY)
        res.sort()
        self.assertEqual(len(res), 5)
        # len is 22 because of header line and trailing '\n'
        self.assertEqual(
            sum([1 for item in open(os.path.join(TEST_DIRECTORY, res[-1]))]),
            22)

    @mock.patch('clients.base.writers.BaseCSVWriter.get_path')
    def test_count_lines(self, get_path):
        test_file = os.path.join(TEST_DIRECTORY, 'line_count.txt')
        get_path.return_value = test_file
        writer = writers.BaseCSVWriter()
        with open(test_file, 'w') as filehandle:
            for _ in range(0, 10):
                filehandle.write('test\n')
        self.assertEqual(writer.count_lines(), 9)

    @mock.patch('clients.base.writers.BaseCSVWriter.get_path')
    def test_get_rotation_path(self, get_path):
        test_file = os.path.join(TEST_DIRECTORY, 'test.csv')
        get_path.return_value = test_file
        writer = writers.BaseCSVWriter()
        # that is not great but it is hard to mock build-in methods
        today = datetime.strftime(datetime.utcnow(), '%Y_%m_%d')
        expected = os.path.join(TEST_DIRECTORY, 'test_'+ today + '_0.csv')
        self.assertEqual(writer.get_rotation_path(), expected)
        # test second
        for item in [1, 2]:
            open(expected, 'w').close()
            expected = os.path.join(
                TEST_DIRECTORY, 'test_{}_{}.csv'.format(today, item))
            self.assertEqual(writer.get_rotation_path(), expected)

    @mock.patch('clients.base.writers.BaseCSVWriter.max_lines', new=3)
    @mock.patch('clients.base.writers.BaseCSVWriter.get_path')
    def test_check_lines(self, get_path):
        test_file = os.path.join(TEST_DIRECTORY, 'test.csv')
        get_path.return_value = test_file
        writer = writers.BaseCSVWriter()
        with open(test_file, 'w') as filehandle:
            for _ in range(0, 5):
                filehandle.write('\n')
        writer.check_lines()
        # that is not great but it is hard to mock build-in methods
        today = datetime.strftime(datetime.utcnow(), '%Y_%m_%d')
        self.assertEqual(
            os.path.join(TEST_DIRECTORY, os.listdir(TEST_DIRECTORY)[0]),
            os.path.join(TEST_DIRECTORY, 'test_'+ today + '_0.csv'))
