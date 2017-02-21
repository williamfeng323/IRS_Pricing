import numpy as np
from scipy import optimize

import utils.utils as util
import utils.bin_tree as btree


def zb_discount(curve='TREASURY_PRICE', interval=.5):
    # retrieve treasury bill/note/bond price from
    #       https://www.treasurydirect.gov/GA-FI/FedInvest/selectSecurityPriceDate.htm
    # compute the discount factor through boot strap method.
    # Interval: the coupon payment frequency.
    zb_price = util.get_rawdata(curve)
    discount = {}
    for key, val in zb_price.items():
        if val['coupon'] == 0:
            discount[key] = val['price'] / 100
        elif key % interval == 0:
            sum_discount = sum(v for k, v in discount.items() if k % interval == 0)
            discount[key] = \
                (val['price']/100 - (val['coupon']*interval) * sum_discount) / \
                (1+val['coupon']*interval)
    # x = list(discount.keys())
    # y = list(discount.values())
    # tck = interpolate.splrep(x, y)
    # xnew = np.arange(0, x[-1], interval)
    # ynew = interpolate.splev(xnew, tck)
    return zb_price, discount


def discount_factor(forward_rates):
    # base on the forward rate calculate discount factors of different maturities.
    # Input example: [.00421, .00431, .00441]
    # Output example: [.99821, .99721, .99631]
    factors = list()
    for ind, val in enumerate(forward_rates):
        factors.append(np.add(1, np.prod(forward_rates[:ind+1])))
    return np.reciprocal(factors)


def expected_value(rate, value_low, value_high, probability):
    return probability*(value_low / (1 + rate)) + (1 - probability) * (value_high / (1 + rate))


def back_count(rate_tree, coupon, interval, par=100, maturity=None, probability=.5):
    # use forward interest rate tree to calculate intrinsic price of the bond
    #
    if maturity is None:
        maturity = len(rate_tree) * interval
    cash_coupon = par * coupon * interval
    value_tree = [[par + cash_coupon] * (len(rate_tree)+1)]
    for ind, val in enumerate(rate_tree[:int(maturity / interval)]):
        nodes = list()
        last_rate = rate_tree[-1 - ind]
        end_value = value_tree[-1]
        for i, v in enumerate(end_value):
            if i < len(end_value) - 1:
                exp_v = expected_value(last_rate[i], end_value[i], end_value[i + 1], probability)
                if len(last_rate) != 1:
                    nodes.append(exp_v + cash_coupon)
                else:
                    nodes.append(exp_v)
        value_tree.append(nodes)
    return value_tree[-1][0]


def bond_value(guess_rate, rate_before, coupon, init_price, interval=.5, sigma=0.43, probability=.5, par=100):
    # Calculate bond value through interest rate path
    # interest rate here is 1 period interest rate at time = t
    # rate_before: the binomial forward interest rate tree before this depth. Example: [[.0034], [.0037,.0041]]
    # guess_rate: the interest rate when the interest rate go low in this period. Example: [.0038]
    # coupon: coupon rate
    # init_price: the bond price observed from market. Set to 0 can compute the theoretical price of the bond
    rate = guess_rate.tolist()
    i = 0
    while i < len(rate_before):
        rate.append(rate[i]*np.exp(sigma*2))
        i += 1
    r = rate_before + [rate]
    return back_count(r, coupon, interval) - init_price


def calibrate_tree(interval=.5, sigma=.13):
    # Create binomial interest rate tree through observed market fixed income instruments
    # Interval: Delta of each step
    # sigma: Assume the sigma is fixed.
    #   Further enhancement plan: Sigma is mean reverse, random term follows brownian motion.
    # Process logic:
    # 1. Retrieve bond price info from market and calculate market discount factors.
    # 2. Calculate market implied forward rate and use as initial guess
    # 3. Back calculate the binomial forward interest rate

    zb_price, discount_set = zb_discount('TREASURY_PRICE', interval)
    implied_forward_rate = list()
    # get discount for every interval
    discounts = list()
    for k, v in discount_set.items():
        if k % interval == 0:
            discounts.append(discount_set[k])
    for i, v in enumerate(discounts):
        if i+1 < len(discounts):
            implied_forward_rate.append(discounts[i]/discounts[i+1]-1)
    implied_forward_rate.insert(0, 1 / discount_set[interval] - 1)
    tree = [[1 / discount_set[interval] - 1]]
    for ind, val in enumerate(implied_forward_rate[:-1]):
        bond = zb_price[interval + interval * (ind + 1)]
        params = (tree[:ind+1], bond['coupon'], bond['price'], interval, sigma)
        print(bond)
        # print(implied_forward_rate[ind+1])
        cal_rate = optimize.fsolve(bond_value, implied_forward_rate[ind+1], args=params)
        nodes = [float(cal_rate)]
        i = 0
        while i < len(tree):
            nodes.append(nodes[i] * np.exp(sigma * 2))
            i += 1
        tree.append(nodes)
    return tree


def draw_tree(rate_tree):
    i = 0
    while i < len(rate_tree):
        last_col = rate_tree[-1]

    return None


def calculate_vnf(coupon, par, maturity, interval):
    rate_tree = calibrate_tree(interval)
    back_count(rate_tree, coupon, interval, par, maturity)
    return None
















