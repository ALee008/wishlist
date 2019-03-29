import os
import sys
import time
import argparse

from loguru import logger
import wishlist.price_alert as price_alert

parser = argparse.ArgumentParser()
parser.add_argument("-p", "--push_api", help="Push bullet custom token. Used to send notifications.")
parser.add_argument("-e", "--export_file", help="Json file path containing youngest wish list info.")
parser.add_argument("-b", "--backup_file", help="Json file path containing the old wish list info.")
parser.add_argument("-l", "--log_path", help="Logfile destination.")
args = parser.parse_args()

if not args.log_path:
    log_path = r"./testdata/price_alert.log"
else:
    log_path = args.log_path

logger.add(log_path, format="{time} {level} {message}",
           level="DEBUG", mode="w")

def get_wish_list_item(list_with_dict, key):
    """
    Return item name from list if exists (key).
    :param list_with_dict: list with wish list item properties in dict.
    :param key: item name
    :return: wish list item if key matches, None else
    """
    try:
        res = [item for item in list_with_dict if item['title'] == key][0]
    except IndexError:
        res = None

    return res


complete_file = os.path.join(os.path.dirname(args.export_file), "complete.txt")
i = 0
while not os.path.exists(complete_file):
    i += 1
    if i > 60:
        logger.info(">>> No complete file found after {} iterations. Exit script with ret code 1.".format(i))
        sys.exit(1)
    time.sleep(60)
    logger.info(">>> No complete file found since {} seconds. Sleep for another 60 seconds.".format(i * 60))

# read latest wish list items
new_wish_list_items = price_alert.read_json(args.export_file)
dict_keys_latest_wish_list = [wish_list_item['title'] for wish_list_item in new_wish_list_items]
# read old wish list items
old_wish_list_items = price_alert.read_json(args.backup_file)
dict_keys_old_wish_list = [wish_list_item['title'] for wish_list_item in old_wish_list_items]

# check latest vs old wish list items and send notification accordingly.
added, removed = price_alert.items_added_or_removed(dict_keys_latest_wish_list, dict_keys_old_wish_list, True)
amazon_prices, used_and_new_offer_prices = (None, None)

for wish_list_item in dict_keys_latest_wish_list:
    old_wish_list_item_data = get_wish_list_item(old_wish_list_items, wish_list_item)
    new_wish_list_item_data = get_wish_list_item(new_wish_list_items, wish_list_item)
    # if item in latest and old wish list check for price difference.
    if old_wish_list_item_data and new_wish_list_item_data:
        alert = price_alert.PriceAlert(new_wish_list_item_data, old_wish_list_item_data, wish_list_item)
        amazon_prices = alert.compare_prices(tolerance=10)
        used_and_new_offer_prices = alert.compare_nauo_prices(tolerance=10)
        # send push bullet notification.
        if args.push_api:
            if amazon_prices:
                resp1 = price_alert.push_message("Amazon Price Alert", amazon_prices, args.push_api)
                logger.info(amazon_prices)
            if used_and_new_offer_prices:
                resp2 = price_alert.push_message("New & Used Price Alert", used_and_new_offer_prices, args.push_api)
                logger.info(used_and_new_offer_prices)

os.remove(complete_file)
logger.info(">>> main_price_alert.py completed successfully.")
