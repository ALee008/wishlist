import os
import sys
import time
import glob
import functools
import wishlist.price_alert as price_alert
from bs4 import BeautifulSoup
from collections import OrderedDict
from wishlist.core import Wishlist, WishlistOffers


def clock(func):
    @functools.wraps(func)
    def clocked(*args, **kwargs):
        t0 = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - t0
        name = func.__name__
        arg_lst = []
        if args:
            arg_lst.append(', '.join(repr(arg) for arg in args))
        if kwargs:
            pairs = ['%s=%r' % (k, w) for k, w in sorted(kwargs.items())]
            arg_lst.append(', '.join(pairs))
        arg_str = ', '.join(arg_lst)
        print('[%0.8fs] %s(%s) -> %r ' % (elapsed, name, arg_str, result))
        return result
    return clocked

@clock
def test(key):
    name = key
    w = Wishlist(name)
    res = []
    for item in w:
        wishlist_offers = item.wishlist_offers.jsonable()
        res.append(wishlist_offers)
        #break
    #print(res)
    return res


def test_offers():

    htmls = glob.glob(os.path.join(r"testdata/de_DE_test", '*.html'))

    for html_doc in htmls:

        with open(html_doc) as html:

            soup = BeautifulSoup(html.read(), 'html.parser')
            w = WishlistOffers('dummy')
            print(w.get_offer_details(str(soup).split(r'<hr class="a-spacing-mini a-divider-normal">')))

#test_offers()
key = "3ATVLKBO1V2CC"

#new_wishlist_items = test(key)

# list_of_wishlist_items = [{'Sabrent USB Externe Soundkarte für Windows und Mac. External Sound Card Stereo Adapter for Windows und Mac. Plug and Play. Keine Treiber erforderlich. (AU-MMSA)':
#         {'title': 'Sabrent USB Externe Soundkarte für Windows und Mac. External Sound Card Stereo Adapter for Windows und Mac. Plug and Play. Keine Treiber erforderlich. (AU-MMSA)', 'price': 5.99, 'item_used_an_new_offers': '2', 'comment': '', 'added': 'Januar 26, 2019', 'rating': 4.3, 'digital': False, 'source': 'marketplace', 'lowest_nauop': OrderedDict([('seller', 'SLJ Trading'), ('price', '4.99'), ('shipping', '0.0'), ('condition', 'Neu')]), 'lowser_nauop_incl_shipping': OrderedDict([('seller', 'SLJ Trading'), ('price', '4.99'), ('shipping', '0.0'), ('condition', 'Neu')])}},
#        {'Neuftech USB RFID Reader ID Kartenlesegerät Kartenleser Kontaktlos Card Reader für EM4100':
#         {'title': 'Neuftech USB RFID Reader ID Kartenlesegerät Kartenleser Kontaktlos Card Reader für EM4100', 'price': 11.49, 'item_used_an_new_offers': '4', 'comment': '', 'added': 'Januar 26, 2019', 'rating': 4.1, 'digital': False, 'source': 'marketplace', 'lowest_nauop': OrderedDict([('seller', 'Aznoi'), ('price', '11.49'), ('shipping', '0.0'), ('condition', 'Neu')]), 'lowser_nauop_incl_shipping': OrderedDict([('seller', 'Aznoi'), ('price', '11.49'), ('shipping', '0.0'), ('condition', 'Neu')])}},
#        {'Simba 107203950 - Squap Fangballspiel 2-er Set, 2-Sortiert, Mehrfarbig':
#             {'title': 'Simba 107203950 - Squap Fangballspiel 2-er Set, 2-Sortiert, Mehrfarbig', 'price': 13.99, 'item_used_an_new_offers': '27', 'comment': '', 'added': 'April 15, 2018', 'rating': 4.3, 'digital': False, 'source': 'marketplace', 'lowest_nauop': OrderedDict([('seller', 'Jumpstore Megastore Online'), ('price', '12.48'), ('shipping', '13.50'), ('condition', 'Neu')]), 'lowser_nauop_incl_shipping': OrderedDict([('seller', 'Amazon.de'), ('price', '13.99'), ('shipping', '0.0'), ('condition', 'Neu')])}}]

# new_wishlist_items = [{'title': 'Sabrent USB Externe Soundkarte', 'price': 77.77, 'item_used_an_new_offers': '2', 'comment': '', 'added': 'Januar 26, 2019', 'rating': 4.3, 'digital': False, 'source': 'marketplace', 'lowest_nauop': OrderedDict([('seller', 'SLJ Trading'), ('price', '4.99'), ('shipping', '0.0'), ('condition', 'Neu')]), 'lowest_nauop_incl_shipping': OrderedDict([('seller', 'SLJ Trading'), ('price', '95.99'), ('shipping', '0.0'), ('condition', 'Neu')])},
#        {'title': 'Neuftech USB RFID Reader ID Kartenlesegerät Kartenleser Kontaktlos Card Reader für EM4100', 'price': 11.49, 'item_used_an_new_offers': '4', 'comment': '', 'added': 'Januar 26, 2019', 'rating': 4.1, 'digital': False, 'source': 'marketplace', 'lowest_nauop': OrderedDict([('seller', 'Aznoi'), ('price', '11.49'), ('shipping', '0.0'), ('condition', 'Neu')]), 'lowest_nauop_incl_shipping': OrderedDict([('seller', 'Aznoi'), ('price', '11.49'), ('shipping', '0.0'), ('condition', 'Neu')])},
#        {'title': 'Simba 107203950 - Squap Fangballspiel 2-er Set, 2-Sortiert, Mehrfarbig', 'price': 13.99, 'item_used_an_new_offers': '27', 'comment': '', 'added': 'April 15, 2018', 'rating': 4.3, 'digital': False, 'source': 'marketplace', 'lowest_nauop': OrderedDict([('seller', 'Jumpstore Megastore Online'), ('price', '12.48'), ('shipping', '13.50'), ('condition', 'Neu')]), 'lowest_nauop_incl_shipping': OrderedDict([('seller', 'Amazon.de'), ('price', '13.99'), ('shipping', '0.0'), ('condition', 'Neu')])}]

# new_wishlist_items = [{'title': 'Neuftech USB RFID Reader ID Kartenlesegerät Kartenleser Kontaktlos Card Reader für EM4100', 'price': 11.49, 'item_used_an_new_offers': '4', 'comment': '', 'added': 'Januar 26, 2019', 'rating': 4.1, 'digital': False, 'source': 'marketplace', 'lowest_nauop': OrderedDict([('seller', 'Aznoi'), ('price', '11.49'), ('shipping', '0.0'), ('condition', 'Neu')]), 'lowest_nauop_incl_shipping': OrderedDict([('seller', 'Aznoi'), ('price', '11.49'), ('shipping', '0.0'), ('condition', 'Neu')])},
#        {'title': 'Simba 107203950 - Squap Fangballspiel 2-er Set, 2-Sortiert, Mehrfarbig', 'price': 19.99, 'item_used_an_new_offers': '27', 'comment': '', 'added': 'April 15, 2018', 'rating': 4.3, 'digital': False, 'source': 'marketplace', 'lowest_nauop': OrderedDict([('seller', 'Jumpstore Megastore Online'), ('price', '12.48'), ('shipping', '13.50'), ('condition', 'Neu')]), 'lowest_nauop_incl_shipping': OrderedDict([('seller', 'Amazon.de'), ('price', '13.99'), ('shipping', '0.0'), ('condition', 'Neu')])},
#                       {'title': 'Squap Fangballspiel 2-er Set, 2-Sortiert, Mehrfarbig',
#                        'price': 9.99, 'item_used_an_new_offers': '27', 'comment': '', 'added': 'April 15, 2018',
#                        'rating': 4.3, 'digital': False, 'source': 'marketplace', 'lowest_nauop': OrderedDict(
#                           [('seller', 'Jumpstore Megastore Online'), ('price', '12.48'), ('shipping', '13.50'),
#                            ('condition', 'Neu')]), 'lowest_nauop_incl_shipping': OrderedDict(
#                           [('seller', 'Amazon.de'), ('price', '13.99'), ('shipping', '0.0'), ('condition', 'Neu')])}]

new_wishlist_items = [
    {
        "title": "A History Of God",
        "price": 10.86,
        "item_used_an_new_offers": "36",
        "comment": "",
        "added": "M\u00e4rz 17, 2019",
        "rating": 3.5,
        "digital": False,
        "source": "marketplace",
        "lowest_nauop": {
            "seller": "Bear Books Germany",
            "price": "0.98",
            "shipping": "8.20",
            "condition": "Gebraucht - Gut"
        },
        "lowest_nauop_incl_shipping": {
            "seller": "UNIVERSALBOOKSLTD",
            "price": "0.77",
            "shipping": "3.00",
            "condition": "Gebraucht - Gut"
        }
    }, ]

# com_data_structure:
#
# [
# 	{item_name#1:
# 		{
# 			title: str, price: float, ..., lowest_nauop:OrderedDict, lowser_nauop_incl_shipping:OrderedDict
# 		}
# 	}
# ,
# 	{item_name#2:
# 		{
# 			title: str, price: float, ..., lowest_nauop:OrderedDict, lowser_nauop_incl_shipping:OrderedDict
# 		}
# 	}
# , ...
# ]


export_file = r"testdata/jsons/export.json"
#price_alert.write_json(new_wishlist_items, export_file)
print("Finished writing to file.")
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

# get keys
dict_keys_latest_wishlist = [wishlist_item['title'] for wishlist_item in new_wishlist_items]
old_wishlist_items = price_alert.read_json(export_file)
dict_keys_old_wishlist = [wishlist_item['title'] for wishlist_item in old_wishlist_items]

added, removed = price_alert.items_added_or_removed(dict_keys_latest_wishlist, dict_keys_old_wishlist, True)

for wishlist_item in dict_keys_latest_wishlist:
    old_wishlist_item_data = get_wishlist_item(old_wishlist_items, wishlist_item)
    new_wishlist_item_data = get_wishlist_item(new_wishlist_items, wishlist_item)
    if old_wishlist_item_data and new_wishlist_item_data:
        alert = price_alert.PriceAlert(new_wishlist_item_data, old_wishlist_item_data, wishlist_item)
        amazon_prices = alert.price_changed
        used_and_new_offer_prices = alert.nauo_price_changed

try:
    pushbullet_api_key = sys.argv[1]
    if pushbullet_api_key:
        if amazon_prices:
            resp1 = price_alert.push_message("Amazon Price Alert", amazon_prices, pushbullet_api_key)
        if used_and_new_offer_prices:
            resp2 = price_alert.push_message("New & Used Price Alert", used_and_new_offer_prices, pushbullet_api_key)
except IndexError:
    pass
