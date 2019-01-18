# -*- coding: utf-8 -*-
from __future__ import unicode_literals, division, print_function, absolute_import
import datetime
import locale
import re
import copy
from contextlib import contextmanager
from collections import namedtuple
import logging

from bs4 import BeautifulSoup, Tag
from brow.interface.selenium import FirefoxBrowser as FullBrowser
from brow.interface.simple import SimpleFirefoxBrowser as SimpleBrowser
from brow.utils import Soup

from .compat import *
from .exception import RobotError, ParseError
from . import environ


logger = logging.getLogger(__name__)
locale.setlocale(locale.LC_ALL, 'deu_deu')

class BaseAmazon(object):
    @property
    def host(self):
        # https://stackoverflow.com/questions/955986/what-is-the-correct-way-to-set-pythons-locale-on-windows/956084#956084
        return "https://www.amazon.de"  #environ.HOST
        #return os.environ.get("WISHLIST_HOST", "https://www.amazon.de")

    def soupify(self, body):
        # https://www.crummy.com/software/BeautifulSoup/
        # docs: https://www.crummy.com/software/BeautifulSoup/bs4/doc/
        # bs4 codebase: http://bazaar.launchpad.net/~leonardr/beautifulsoup/bs4/files
        if isinstance(body, Tag): return body
        soup = Soup(body)
        return soup

    def dump(self):
        return self.soup.prettify()


class WishlistElement(BaseAmazon):
    """Wishlist.get() returns an instance of this object"""
    @property
    def uuid(self):
        uuid = self.a_uuid
        if not uuid:
            uuid = self.external_uuid
        return uuid

    @property
    def url(self):
        url = self.a_url
        if not url:
            url = self.external_url
        return url

    @property
    def a_uuid(self):
        """return the amazon uuid of the item"""
        uuid = ""
        a_url = self.url
        if a_url:
            m = re.search("/dp/([^/\?\&]+)", self.url)
            if m:
                uuid = m.group(1)
        else:
            # go through all the a tags in ItemInfo looking for asin=
            el = self.soup.find("div", id=re.compile("^itemInfo_"))
            if el:
                regex = re.compile("asin\=([^\&]+)")
                els = el.findAll("a", {"href": regex})
                for el in els:
                    m = regex.search(el.attrs["href"])
                    if m:
                        uuid = m.group(1).strip()
                        if uuid: break
        return uuid

    @property
    def a_url(self):
        """return the amazon url of the item"""
        href = ""
        # http://stackoverflow.com/questions/5041008/how-to-find-elements-by-class
        # http://stackoverflow.com/a/5099355/5006
        # http://stackoverflow.com/a/2832635/5006
        el = self.soup.find("a", id=re.compile("^itemName_"))
        if el and ("href" in el.attrs):
            href = self.host + el.attrs["href"]
        return href

    @property
    def external_uuid(self):
        """Return the external uuid of the item"""
        ext_url = self.external_url
        return md5(ext_url) if ext_url else ""

    @property
    def external_url(self):
        """was this added from an external website? Then this returns that url"""
        href = ""
        el = self.soup.find("span", {"class": "clip-text"})
        if not el:
            el = self.soup.select_one("[id^=item_from]")
        if el:
            el = el.find("a")
            if el:
                href = el.attrs.get("href", "")

        return href.strip()

    @property
    def image(self):
        src = ""
        imgs = self.soup.find_all("img")
        for img in imgs:
            if "src" in img.attrs:
                if img.parent and img.parent.name == "a":
                    a = img.parent
                    if a.attrs["href"].startswith("/dp/"):
                        src = img.attrs["src"]
                        break

        if not src:
            for img in imgs:
                maybe_src = img.attrs.get("src", "")
                if "/images/I/" in maybe_src:
                    src = maybe_src
                    break

        return src

    @property
    def price(self):
        price = 0.0

        el = self.soup.find("span", id=re.compile(r"^itemPrice_"))

        if el and len(el.contents) >= 1:
            # the new HTML actually has separate spans for whole currency
            # units and fractional currency units
            try:
                whole = float(
                    el.find(
                        'span', class_='a-price-whole'
                    ).contents[0].strip().replace(',', '')
                )
                fract = float(
                    el.find('span', class_='a-price-fraction').contents[0].strip()
                )
                price = float(whole) + (float(fract) / 100.0)

            except AttributeError:
                try:
                    s = "".join(el.strings).split("-")[0].strip()
                    price = float(s.lstrip('$').replace(",", ""))
                except ValueError:
                    price = 0.0

        else:
            in_stock = True
            el_available = self.soup.find("div", class_="itemAvailability")
            if el_available:
                if el_available.find("span", class_="itemAvailMessage"):
                    if el_available.find("a", class_="itemAvailSignup"):
                        in_stock = True

            if not in_stock:
                raise ParseError(
                    msg="Could not find price for {}".format(self.title),
                    body=self.body
                )

        return price

    @property
    def marketplace_price(self):
        price = 0.0
        el = self.soup.find("span", {"class": "itemUsedAndNewPrice"})
        if el and len(el.contents) > 0:
            # marketplace price decimal separator might be ',' or '.' depending on locale.
            match = re.match(r".+(\d+\.|\,\d+)", el.contents[0])
            # replace decimal separator ',' with '.'
            marketplace_price = match.group().replace(',', '.') if match else 0.0
            price = float(marketplace_price)
        return price

    @property
    def item_used_and_new_url(self):
        href = ""
        el = self.soup.find(class_=re.compile("^itemUsedAndNewLink"))
        if el and ("href" in el.attrs):
            href = self.host + el.attrs["href"]
        # if no new_and_used offer exists return None
        return href or None

    @property
    def item_used_and_new_offers(self):
        el = self.soup.find(class_=re.compile("^itemUsedAndNewLink"))
        if el:
            match = re.match(r"\d+", el.contents[0])
            offers = match.group()
        else:
            offers = None

        return offers

    @property
    def item_used_and_new_soup(self):
        url = self.item_used_and_new_url
        if not url:
            return None
        with SimpleBrowser.session() as b:
            b.load(url)
            b.dump(self.title.replace(' ', '.'))
            soup = b.soup
        return soup

    @property
    def title(self):
        title = ""
        el = self.soup.find("a", id=re.compile("^itemName_"))
        if el and len(el.contents) > 0:
            title = el.contents[0].strip()

        else:
            el = self.soup.find("span", id=re.compile("^itemName_"))
            if el and len(el.contents) > 0:
                title = el.contents[0].strip()

        return title

    @property
    def comment(self):
        ret = ""
        el = self.soup.find("span", id=re.compile("^itemComment_"))
        if el and len(el.contents) > 0:
            ret = el.contents[0].strip()
        return ret

    @property
    def rating(self):
        stars = 0.0
        el = self.soup.find("a", {"class": "reviewStarsPopoverLink"})
        if el:
            el = el.find("span", {"class": "a-icon-alt"})
            if len(el.contents) > 0:
                stars = float(el.contents[0].strip().split()[0])
        return stars

    @property
    def author(self):
        el = self.soup.find("a", id=re.compile("^itemName_"))
        if not el:
            return ''
        author = el.parent.next_sibling
        if author is None or len(author.contents) < 1:
            return ''
        return author.contents[0].strip().replace("by ", "")

    @property
    def added(self):
        ret = None
        _locale, _ = locale.getlocale()
        if _locale == 'de_DE':
            format_str = '%d. %B %Y'
        else:
            format_str = '%B %d, %Y'
        el = self.soup.find('span', id=re.compile('^itemAddedDate_'))
        if el is None or len(el.contents) < 3:
            el = self.soup.select_one(".dateAddedText > span")
            if el:
                s = el.get_text().strip()
                while s:
                    try:
                        ret = datetime.datetime.strptime(s, format_str)
                        break

                    except ValueError:
                        bits = s.split(" ", 1)
                        if len(bits) > 1:
                            s = " ".join(bits[1:])
                        else:
                            s = ""

                if not ret:
                    logger.error('Unable to find added date for item.')

        else:
            ret = datetime.datetime.strptime(el.contents[2].strip(), format_str)

        return ret

    @property
    def wanted_count(self):
        """returns the wanted portion of .quantity"""
        return self.quantity[0]

    @property
    def has_count(self):
        """Returns the has portion of .quantity"""
        return self.quantity[1]

    @property
    def quantity(self):
        """Return the quantity wanted and owned of the element

        :returns: tuple of ints (wanted, has)
        """
        ret = None
        el = self.soup.find(id=re.compile("^itemQuantityRow_"))
        bits = [s for s in el.stripped_strings]
        if len(bits) == 4:
            ret = (int(bits[1]), int(bits[3]))

        elif len(bits) == 2:
            ret = (0, 0)

        else:
            raise ParseError(
                msg="Could not find quantity for {}".format(self.title),
                body=self.body
            )

        return ret

    @property
    def source(self):
        """Return "amazon" if product is offered by amazon, otherwise return "marketplace" """
        ret = "marketplace"
        if not self.is_digital():
            el = self.soup.find(class_=re.compile("^itemAvailOfferedBy"))
            if el:
                s = el.string
                # In Stock. Offered by Amazon.com.
                if s and re.search(r"amazon\.com", s, re.I):
                    ret = "amazon"
        return ret

    @property
    def body(self):
        return self.soup.prettify()

    @property
    def page_url(self):
        ret = self._page_url
        if ret:
            el = self.soup.find(id=re.compile("^itemMain_"))
            if el:
                ret += "#{}".format(el.attrs["id"])
        return ret

    def __init__(self, element, page_url="", page=0):
        """
        :param element: mixed, the html for the element
        :param page_url: string, the current page url
        :param page: int, the current page number
        """
        self.soup = self.soupify(element)
        self._page_url = page_url
        self.page = int(page)

    def is_digital(self):
        """Return true if this is a digital good like a Kindle book or mp3"""
        ret = False
        el = self.soup.find(class_=re.compile("^itemAvailOfferedBy"))
        if not el:
            el = self.soup.find(class_=re.compile("^itemAvailability"))

        if el:
            s = "".join(el.strings)
            if s:
                ret = True
                if not re.search(r"auto-delivered\s+wirelessly", s, re.I):
                    if not re.search(r"amazon\s+digital\s+services", s, re.I):
                        ret = False
        return ret

    def in_stock(self):
        """Return True if the item is in stock"""
        return self.price or self.is_digital()

    def is_amazon(self):
        """returns True if product is offered by amazon, otherwise False"""
        return "amazon" in self.source

    def jsonable(self):
        json_item = {}
        json_item["title"] = self.title
        json_item["price"] = self.price
        json_item["item_used_an_new_offers"] = self.item_used_and_new_offers
        json_item["comment"] = self.comment
        json_item["added"] = self.added.strftime('%B %d, %Y')
        json_item["rating"] = self.rating
        json_item["digital"] = self.is_digital()
        json_item["source"] = self.source
        new_and_used_offers = WishlistOffers(self)
        # nauo = new and used offer price
        json_item["lowest_nauop"], json_item["lowser_nauop_incl_shipping"] = new_and_used_offers.lowest_offer
        return json_item

class WishlistOffers(BaseAmazon):
    """
    """
    def __init__(self, wishlist_element):

        self.wishlist_element = wishlist_element
        #print(self.wishlist_element.title)

        self.marketplaces_details = namedtuple('marketplaces_details', [
            'seller',
            'price',
            'shipping',
            'condition'
        ])

    @staticmethod
    def get_price_from_string(price_as_string):
        match = re.search(r"\d+(\,|\.)\d+", price_as_string)
        if match:
            return match.group()
        else:
            return None

    @property
    def offers_details(self):

        res = []

        offers_wishlist_soup = self.wishlist_element.item_used_and_new_soup

        if offers_wishlist_soup:
            html_doc = str(offers_wishlist_soup).split(r'<hr class="a-spacing-mini a-divider-normal">')
        else:
            # in case no new and used item offers exist
            print('No new_and_used offers for <<%s>> available.' % self.wishlist_element.title)
            res.append(self.marketplaces_details('N/A', '0.0', '0.0', ''))
            return res

        for html_part in html_doc:

            soup = BeautifulSoup(html_part, 'html.parser')

            seller_name = soup.find('h3', attrs={'class': 'olpSellerName'})
            if not seller_name:
                continue
            if seller_name.span:
                seller = seller_name.a.string.strip()
            else:
                seller = seller_name.img.attrs['alt']
            offer_price = self.get_price_from_string(soup.find('span', attrs={'class': 'olpOfferPrice'}).string.strip())
            offer_shipping_info = soup.find_all('p', attrs={'class', 'olpShippingInfo'})

            def get_shipping_costs():
                # if olpShippingInfo is empty/None in most cases due to 'prime' and thus free delivery.
                if not offer_shipping_info:
                    return '0,0'
                for shipping_info in offer_shipping_info:
                    for element in shipping_info.span.children:
                        if isinstance(element, Tag):
                            shipping_cost_from_string = self.get_price_from_string(element.next_element.string.strip())
                            # TODO: fix locale dependency
                            return shipping_cost_from_string or '0,0'  # if None return 0,0
                        # TODO: fix locale dependency
                        elif element.string.strip().upper() in [u'KOSTENLOSE LIEFERUNG', u'KOSTENFREIE LIEFERUNG']:
                            return '0,0'  # TODO: fix locale dependency

            offer_condition = soup.find('span', attrs={'class': 'olpCondition'})
            shipping_cost = get_shipping_costs() or '0,0'

            res.append(self.marketplaces_details(seller,
                                                 # because of localization 24,99 to 24.99
                                                 offer_price.replace(',', '.'),
                                                 shipping_cost.replace(',', '.'),
                                                 re.sub(r'\s+\-', ' -', offer_condition.string.strip())
                                                 ))

        return res

    @property
    def lowest_offer(self):
        """
        """
        offers_details = copy.deepcopy(self.offers_details)

        lowest_offer = min(offers_details, key=lambda x: x.price)
        lowest_offer_incl_shipping = min(offers_details, key=lambda x: (float(x.price) + float(x.shipping)))

        return lowest_offer, lowest_offer_incl_shipping


class Wishlist(BaseAmazon):
    """Wrapper that is specifically designed for getting amazon wishlists"""

    element_class = WishlistElement

    @classmethod
    @contextmanager
    def authenticate(cls):
        host = environ.HOST
        logger.info("Requesting {}".format(host))
        with FullBrowser.session() as b:
            b.load(host, ignore_cookies=True)
            yield b

    def __init__(self, name):
        self.name = name

    def robot_check(self, soup):
        el = soup.find("form", action=re.compile(r"validateCaptcha", re.I))
        if el:
            raise RobotError("Amazon robot check")

    def get_wishlist_url(self, path=""):
        if not path:
            name = self.name
            path = "/gp/registry/wishlist/{}".format(name)
        return "{}/{}".format(self.host.rstrip("/"), path.lstrip("/"))

    def get_items(self, soup, current_page_url, current_page=0):
        """this will return the wishlist elements on the current page"""
        html_items = soup.findAll("div", {"id": re.compile("^item_")})
        for i, html_item in enumerate(html_items):
            item = self.element_class(html_item, current_page_url, current_page)
            yield item

    def __iter__(self):
        host = self.host
        # so the lists are circular for some reason, so we need to track what pages
        # we have seen and stop when we see the item uuid again
        name = self.name
        seen_uuids = set()
        url = self.get_wishlist_url()
        with SimpleBrowser.session() as b:
            page = 1
            while url:
                b.load(url)
                # b.dump(directory="{}-{}".format(name, page))
                b.dump()
                soup = b.soup

                for item in self.get_items(soup, url, page):
                    yield item

                url = ""
                uuid_elem = soup.select_one("input#sort-by-price-lek")
                if uuid_elem:
                    uuid = uuid_elem.get("value")
                    if uuid:
                        elem = soup.select_one("input#sort-by-price-load-more-items-url")
                        if uuid not in seen_uuids:
                            logger.debug("First time seeing uuid {}".format(uuid))
                            url = self.get_wishlist_url(elem["value"])
                            seen_uuids.add(uuid)
                            page += 1

