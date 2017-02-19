import numpy as np
from binarytree import tree, pprint, inspect
from scipy import interpolate
import utils.utils as util


def zb_discount(curve='TREASURY_PRICE', interval=.5):
    zb_price = util.get_rawdata(curve)
    discount = {}
    for key, val in zb_price.items():
        if val['coupon'] == 0:
            discount[key] = val['price'] / 100
        elif key % interval == 0:
            sum_discount = sum(v for k, v in discount.items() if k % interval==0)
            discount[key] = \
                (val['price']/100 - (val['coupon']*interval) * sum_discount) / \
                (1+val['coupon']*interval)
    x = list(discount.keys())
    y = list(discount.values())
    tck = interpolate.splrep(x, y)
    xnew = np.arange(0, x[-1], interval)
    ynew = interpolate.splev(xnew, tck)
    return zb_price, discount, xnew, ynew, tck


def discount_factor(forward_rates):
    factors =[]
    for ind, val in enumerate(forward_rates):
        factors.append(1,np.prod(forward_rates[:ind+1]))
    return np.reciprocal(factors)


def bond_value(r, sigma, coupon, maturity, probability=.5, par=100):
    # sample of r: {.5: .0034, 1: .0037}
    if type(r) is not type(dict) or list(r.keys())[-1] != maturity:
        raise Exception(TypeError, r)
    # construct low/high interest rate discount factors
    discount_low = discount_factor(list(r.values()))
    discount_high = discount_factor(np.multiply(list(r.values()), np.exp(2*sigma)))
    cash_coupon = coupon * par
    price = probability*(cash_coupon*sum(discount_low[:-1]) + (cash_coupon+par) / discount_low[-1])
    + (1 - probability) * (cash_coupon*sum(discount_high[:-1]) + (cash_coupon+par) / discount_high[-1])
    return price


def calibrate_tree():

    return None