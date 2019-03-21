import json
import requests

class PriceAlert:

    def __init__(self, latest_item_call, old_item_call, item):
        """

        :param latest_item_call: Wishlist element data from latest fetch.
        :param old_item_call: Wishlist element data stored in json file.
        """
        self.item_name = item
        self.old_item_price = old_item_call['price']
        self.new_item_price = latest_item_call['price']
        self.relative_price_difference = self.get_relative_price_difference(self.new_item_price, self.old_item_price)
        # new and used offer price including shipping costs
        self.old_nauo_price = float(old_item_call['lowest_nauop_incl_shipping']['price'])
        self.new_nauo_price = float(latest_item_call['lowest_nauop_incl_shipping']['price'])
        self.relative_nauo_price_difference = self.get_relative_price_difference(self.new_nauo_price, self.old_nauo_price)

    def prepare_wishlist_dict(self):
        pass

    @staticmethod
    def get_relative_price_difference(new_price, old_price):
        """
        calculate relative price change between new and old price, considering sign.
        :param new_price: price from latest wishlist fetch.
        :param old_price: price from data stored in json.
        :return: (float) relative price difference.
        """
        try:
            return float((new_price - old_price) / old_price) * 100
        except ZeroDivisionError:
            return 1.0 * 100

    def compare_nauo_prices(self):
        """
        Return True if nauo price from last fetch <> stored nauo price
        :return: (bool)
        """
        if abs(self.new_nauo_price - self.old_nauo_price) < 0.00001:
            return False
        else:
            msg = "New and used price offer for \"{}\" changed from {:.2f},- to {:.2f},-. Price difference {:.2f}%."\
                .format(self.item_name, self.old_nauo_price, self.new_nauo_price, self.relative_nauo_price_difference)
            print(msg)
            return msg

    def compare_prices(self):
        """
        Return True if price from last fetch <> stored price
        :return: (bool)
        """
        if abs(self.new_item_price - self.old_item_price) < 0.00001:
            return False
        else:
            msg = "Amazon price for \"{}\" changed from {:.2f},- to {:.2f},-. Price difference {:.2f}%.".format(
                self.item_name, self.old_item_price, self.new_item_price, self.relative_price_difference)
            print(msg)
            return msg

    price_changed = property(compare_prices)
    nauo_price_changed = property(compare_nauo_prices)


def write_json(jsonable, json_file):

    with open(json_file, 'w') as outf:
        json.dump(jsonable, outf, indent=4)

    print("Finished writing to {}".format(json_file))
    return None


def read_json(json_file):

    with open(json_file, 'r') as infile:
        res = json.load(infile)

    return res


# Send a message to all your registered devices.
def push_message(title, body, api_key):
    data = {
        'type': 'note',
        'title': title,
        'body': body
    }
    resp = requests.post('https://api.pushbullet.com/api/pushes', data=data, auth=(api_key, ''))

    return None

def items_added_or_removed(latest_wishlist_items, old_wishlist_items, verbose):
    """
    Return added and removed items to/from wishlist compared to last run.
    :param latest_wishlist_items: list of items from latest run.
    :param old_wishlist_items: list of items from older run.
    :param verbose: (bool) if True print added/removed items.
    :return: (set) added and removed items
    """
    latest_items = set(latest_wishlist_items)
    old_items = set(old_wishlist_items)

    added = latest_items.difference(old_items)
    removed = old_items.difference(latest_items)

    if verbose:
        # some item descriptions contain commas. These are replaced by "|" to prevent
        # confusion as set is printed.
        if added:
            print("{0} new item(s) added to wish list since last run: {1}"
                  .format(len(added), added).replace(",", " |"))
        if removed:
            print("{0} item(s) removed from wish list since last run: {1}"
                  .format(len(removed), removed).replace(",", " |"))

    return added, removed
