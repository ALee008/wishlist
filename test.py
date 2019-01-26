import os
import time
import glob
import functools
from bs4 import BeautifulSoup
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
    i = 0
    for item in w:
        res.append(item.jsonable())
        i += 1
    print(res)
    print('# items', i)


def test_offers():

    htmls = glob.glob(os.path.join(r"testdata/de_DE_test", '*.html'))

    for html_doc in htmls:

        with open(html_doc) as html:

            soup = BeautifulSoup(html.read(), 'html.parser')
            w = WishlistOffers('dummy')
            print(w.get_offer_details(str(soup).split(r'<hr class="a-spacing-mini a-divider-normal">')))

key = "KEY_HERE"

test(key)