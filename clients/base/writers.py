# pylint:disable=R0201,W0613
"""
Base classes to write data.
"""
# standard library
import os
# project
from clients.base import parsers


class BaseCSVWriter():
    """
    Writes data to CSV
    """
    header = []
    template = ''
    parser_class = parsers.BaseParser

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
