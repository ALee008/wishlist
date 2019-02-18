import json

class PriceAlert:

    def __init__(self, latest_item_call, old_item_call):
        """

        :param latest_item_call: Wishlist element data from latest fetch.
        :param old_item_call: Wishlist element data stored in json file.
        """
        self.old_item_price = old_item_call['price']
        self.new_item_price = latest_item_call['price']
        self.relevative_price_difference = self.relative_price_difference(self.new_item_price, self.old_item_price)
        # new and used offer price including shipping costs
        self.old_nauo_price = float(old_item_call['lowest_nauop_incl_shipping']['price'])
        self.new_nauo_price = float(latest_item_call['lowest_nauop_incl_shipping']['price'])
        self.relevative_nauo_price_difference = self.relative_price_difference(self.new_nauo_price, self.old_nauo_price)

    def prepare_wishlist_dict(self):
        pass

    @staticmethod
    def relative_price_difference(new_price, old_price):
        """
        calculate relative price change between new and old price, considering sign.
        :param new_price: price from latest wishlist fetch.
        :param old_price: price from data stored in json.
        :return: (float) relative price difference.
        """
        return float((new_price - old_price) / new_price)

    def compare_nauo_prices(self):
        """
        Return True if nauo price from last fetch <> stored nauo price
        :return: (bool)
        """
        if abs(self.new_nauo_price - self.old_nauo_price) < 0.00001:
            return False
        else:
            return True

    def compare_prices(self):
        """
        Return True if price from last fetch <> stored price
        :return: (bool)
        """
        if abs(self.new_item_price - self.old_item_price) < 0.00001:
            return False
        else:
            return True

    def send_notification(self):
        pass

    price_changed = property(compare_prices)
    nauo_price_changed = property(compare_nauo_prices)


def write_json(jsonable, json_file):

    with open(json_file, 'w') as outf:
        json.dump(jsonable, outf, indent=4)

    return None


def read_json(json_file):

    with open(json_file, 'r') as infile:
        res = json.load(infile)

    return res

