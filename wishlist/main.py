import argparse
from wishlist.core import Wishlist
import wishlist.price_alert as price_alert

parser = argparse.ArgumentParser()
parser.add_argument("-k", "--key", help="Amazon wish list key (check wish list url)")
parser.add_argument("-p", "--push_api", help="Push bullet custom token. Used to send notifications.")
parser.add_argument("-e", "--export_file", help="Json file path containing wish list info.")
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
        #break
    #print(res)
    return res


def get_wishlist_item(list_with_dict, key):
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


new_wish_list_items = get_wish_list_items(args.key)

if args.export_file:
    export_file = args.export_file
else:
    export_file = r"../testdata/jsons/export.json"

# write wish list info to file.
# price_alert.write_json(new_wish_list_items, export_file)

# get item name
dict_keys_latest_wish_list = [wish_list_item['title'] for wish_list_item in new_wish_list_items]
old_wish_list_items = price_alert.read_json(export_file)
dict_keys_old_wish_list = [wish_list_item['title'] for wish_list_item in old_wish_list_items]

added, removed = price_alert.items_added_or_removed(dict_keys_latest_wish_list, dict_keys_old_wish_list, True)

for wish_list_item in dict_keys_latest_wish_list:
    old_wish_list_item_data = get_wishlist_item(old_wish_list_items, wish_list_item)
    new_wish_list_item_data = get_wishlist_item(new_wish_list_items, wish_list_item)
    if old_wish_list_item_data and new_wish_list_item_data:
        alert = price_alert.PriceAlert(new_wish_list_item_data, old_wish_list_item_data, wish_list_item)
        amazon_prices = alert.price_changed
        used_and_new_offer_prices = alert.nauo_price_changed

if args.push_api:
    if amazon_prices:
        resp1 = price_alert.push_message("Amazon Price Alert", amazon_prices, args.push_api)
    if used_and_new_offer_prices:
        resp2 = price_alert.push_message("New & Used Price Alert", used_and_new_offer_prices, args.push_api)
