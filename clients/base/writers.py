# pylint:disable=R0201,W0613
"""
Base classes to write data.
"""
# standard library
from datetime import datetime
import os
import shutil
# project
from clients.base import parsers


class BaseCSVWriter():
    """
    Writes data to CSV
    """
    header = []
    template = ''
    parser_class = parsers.BaseParser
    max_lines = -1

    def __init__(self):
        print('Write to', self.get_path())

    def add_to_csv(self, msg):
        """
        Adds a message as line to a CSV file. Provide self.parser_class to
        transform msg to a flat dictionary. The header will pick which values
        will be put into the CSV.

        Args:
            msg(paho-mqtt.message): A MQTT message (or any message the parser
                can digetst)
        Returns:
            None
        """
        csv_line = self.serialize(msg)
        # we need this to enable multiple csv for the same
        # reason file generation is in the storage process
        path = self.get_path()
        print(path)
        if self.max_lines > 0:
            self.check_lines()
        if not os.path.isfile(path):
            self.create_csv(path, self.header)
        print('Add line to', path)
        with open(path, 'a') as filehandle:
            filehandle.write(csv_line)

    def create_csv_line(self, dic):
        """
        Picks fields from a dict and creates CSV line according header.

        Args:
            dic(dict): The input dictionary
        Returns:
            str
        """
        return ','.join([
            str(dic.get(field, '')) for field in self.header]) + '\n'

    def serialize(self, msg):
        """
        Serializes Message to CSV line

        Args:
            msg(paho-mqtt.message)
        Returns:
            str
        """
        dic = self.parser_class().parse(msg)
        return self.create_csv_line(dic)

    def get_path(self):
        """
        Returns full path for destination file
        """
        return self.template

    def create_csv(self, path, header):
        """
        Create a new CSV file (and directories)

        Args:
            path(str): destination path
            header(list): fields in the header
        Returns:
            None
        """
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as filehandle:
            filehandle.write(','.join(header) + '\n')

    def get_rotation_path(self):
        """
        This secures that data does not get overriden when backed up on the
        same day. Will probably be used very rarely but it supports quick
        testing.

        Returns:
            str
        """
        # somewhat ugly: TODO: clean-up
        path = self.get_path()
        part, ext = os.path.splitext(path)
        date = datetime.strftime(datetime.utcnow(), '%Y_%m_%d')
        new_name = '{}_{}_0{}'.format(part, date, ext)
        counter = 0
        while os.path.isfile(new_name):
            counter += 1
            part, ext = os.path.splitext(new_name)
            new_name = '{}_{}{}'.format(part[:-2], counter, ext)
        return new_name

    def count_lines(self):
        """
        Count lines for limiting file_size

        Returns int
        """
        return sum(1 for line in open(self.get_path())) - 1

    def check_lines(self):
        """
        Check and move file if self.max_lines is reached

        Returns:
            None
        """
        path = self.get_path()
        if os.path.isfile(path) and self.max_lines < self.count_lines():
            shutil.move(self.get_path(), self.get_rotation_path())
