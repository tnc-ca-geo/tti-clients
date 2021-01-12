# standard library
import os
# project
from clients.base import parsers


class BaseCSVWriter():
    header = []
    template = ''
    parser_class = parsers.BaseParser

    def add_to_csv(self, msg):
        csv_line = self.serialize(msg, header=self.header)
        # we need this to enable multiple csv for the same
        # reason file generation is in the storage process
        path = self.get_path()
        print(path)
        if not os.path.isfile(path):
            self.create_csv(path, self.header)
        print('Add line to', path)
        with open(path, 'a') as filehandle:
            filehandle.write(csv_line + '\n')

    def create_csv_line(self, dic):
        return ','.join([
            str(dic.get(field, '')) for field in self.header])

    def serialize(self, msg, header=[]):
        dic = self.parser_class().parse(msg)
        return self.create_csv_line(dic)

    def get_path(self):
        return self.template

    def create_csv(self, path, header):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, 'w') as filehandle:
            filehandle.write(','.join(header) + '\n')
