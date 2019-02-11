import json
from collections import OrderedDict


class PriceAlert:

    def __init__(self):
        pass

    def write_json(self, jsonable, json_file):

        with open(json_file, 'w') as outf:
            for item in jsonable:
                json.dump(item, outf, indent=4)

        return None

    def read_json(self, json_file):

        with open(json_file, 'r') as infile:
            res = json.load(infile)

        return res

    def compare_prices(self):
        pass

    def send_notification(self):
        pass
