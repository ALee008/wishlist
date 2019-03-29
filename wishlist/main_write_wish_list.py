import os
import argparse
from loguru import logger
from wishlist.core import Wishlist
import wishlist.price_alert as price_alert

logger.add("/home/ali/bin/log/write_wish_list.log", format="{time} {level} {message}",
           level="DEBUG", rotation="1 MB")

parser = argparse.ArgumentParser()
parser.add_argument("-k", "--key", help="Amazon wish list key (check wish list url)")
parser.add_argument("-e", "--export_file", help="Json file path containing wish list info.")
parser.add_argument("-t", "--test", action="store_true", help="Amazon wish list key (check wish list url)")
args = parser.parse_args()


def get_wish_list_items(key):
    """
    Return items from amazon wish list using key (part of wish list url).
    :param key: (string) wish list key
    :return: (list) list of dict. Each dict represents an item from wish list. Item name (key) -> Item info (value).
    """
    name = key
    w = Wishlist(name)
    res = []
    for item in w:
        wish_list_offers = item.wishlist_offers.jsonable()
        res.append(wish_list_offers)
        if args.test:
            print(res)
            break
    return res


def write_complete(path):
    """
    Write a complete file. Needed to signal, that job is done.
    :param path: (str) path for complete.txt
    :return: None
    """
    complete_file = os.path.join(path, "complete.txt")
    with open(complete_file, "w") as comp:
        comp.write("Finished")

    return None


if args.export_file:
    export_file = args.export_file
else:
    export_file = r"../testdata/jsons/export.json"

new_wish_list_items = get_wish_list_items(args.key)

# write wish list info to file.
price_alert.write_json(new_wish_list_items, export_file)
write_complete(os.path.dirname(export_file))
