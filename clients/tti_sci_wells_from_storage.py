"""
Use the storage API instead of MQTT to get data from the wells application
"""
# standard
import os
# project
from clients.base import storage, parsers, writers
from clients.tti_sci_wells import TBS12SinSituCSVWriter


OUTPUT_TEMPLATE = os.path.join(os.path.expanduser("~"),
    'lora_data', os.path.splitext(os.path.split(__file__)[1])[0] + '.csv')


class MyStorageReader(storage.StorageReader):
    """
    Configure storage reader
    """
    url = (
        'https://tnc.nam1.cloud.thethings.industries/'
        'api/v3/as/applications/sci-wells/packages/storage/uplink_message')


class TBS12SinSituFromStorageWriter(TBS12SinSituCSVWriter):
    """
    Make sure we overwrite and don't append
    """
    append = False
    template = OUTPUT_TEMPLATE


if __name__ == '__main__':
    writer = TBS12SinSituFromStorageWriter()
    MyStorageReader(callback=writer.add_to_csv).run()
