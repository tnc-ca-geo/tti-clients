# pylint:disable=E0401
"""
Read data from storage API with utmost compatibility to the mqtt client
"""
# standard library
from datetime import datetime, timedelta
import json
import os
from types import SimpleNamespace
# third party
import requests


class StorageReader():
    """
    Read historic data from ThingsIndustries storage integration
    """
    url = None
    pw_env_var = 'MQTT_PW'
    start = datetime(2021, 3, 18)

    def __init__(self, password=None, callback=None):
        self.password = password or os.environ.get(self.pw_env_var)
        self.callback = callback

    def reformat(self, line):
        """
        This becomes necessary for compatibility
        """
        try:
            dic = json.loads(line)
        except json.decoder.JSONDecodeError:
            return None
        part = dic.get('result')
        if part:
            return json.dumps(part)
        return None

    def record_generator(self):
        """
        Generate records to be processed. For simplicity we are doing this
        synchronlously and paginate by day
        """
        headers = {'Authorization': 'Bearer {}'.format(self.password)}
        time = self.start
        while time < datetime.utcnow():
            print('Loading new page')
            after = time.strftime('%Y-%m-%dT%H:%M:%SZ')
            time = time + timedelta(days=1)
            before = time.strftime('%Y-%m-%dT%H:%M:%SZ')
            res = requests.get(
                self.url, headers=headers, params={'after': after, 'before': before})
            if res.status_code == 200:
                for line in res.text.split('\n'):
                    line = self.reformat(line)
                    if line:
                        yield SimpleNamespace(payload=line.encode('utf-8'))
            else:
                print(res.status_code, res.text)
                break


    def run(self):
        """
        Process data from storage API. Naming is for compatibility with
        MQTT client
        """
        for item in self.record_generator():
            try:
                self.callback(item)
            except:
                print(item)
                break
