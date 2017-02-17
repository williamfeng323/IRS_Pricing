import numpy as np
from binarytree import tree, pprint, inspect
import utils.utils as util


def zb_discount(curve='TREASURY_PRICE', interval=.5):
    spot_curve = util.get_rawdata(curve)
    discount = {}
    for key, val in spot_curve.items():
        if val['coupon'] == 0:
            discount[key] = val['price'] / 100
        elif key % interval == 0:
            sum_discount = sum(v for k,v in discount.items() if k % interval==0)
            print(sum_discount)
            discount[key] = \
                (val['price']/100 - (val['coupon']*interval) * sum_discount) / \
                (1+val['coupon']*interval)
    return discount
