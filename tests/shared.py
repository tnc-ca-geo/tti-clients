# pylint:disable=C0115
"""
Shared test classes
"""
# standard library
import os
import shutil
from types import SimpleNamespace
from unittest import TestCase


TEST_DIRECTORY = os.path.join(os.path.dirname(__file__), 'test_directory')


class PayloadTestCase(TestCase):
    example_payload = 'tti_sci_chi_example_payload.txt'

    def setUp(self):
        """
        Load exampe payload from a file
        """
        example_filename = os.path.join(
            os.path.dirname(__file__), self.example_payload)
        with open(example_filename, 'rb') as file_handle:
            example_payload = file_handle.read()
        self.example_message = SimpleNamespace(payload=example_payload)
        os.makedirs(TEST_DIRECTORY, exist_ok=True)

    def tearDown(self):
        shutil.rmtree(TEST_DIRECTORY)
