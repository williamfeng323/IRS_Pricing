import numpy as np
from scipy import interpolate
from scipy import optimize
import utils.utils as util


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
    factors = []
    for ind, val in enumerate(forward_rates):
        factors.append(np.add(1, np.prod(forward_rates[:ind+1])))
    return np.reciprocal(factors)


def bond_value(rate, rate_before, coupon, init_price, sigma=0.43, probability=.5, par=100):
    # Calculate bond value through interest rate path
    # price = P of interest rate down * sum of (cash flow * discount factors)
    #           + P of interest rate up * sum of (cash flow * discount factors)
    # rate_before: the interest rate path before this period. Example: [.0034, .0037]
    # r: the interest rate when the interest rate go low in this period. Example: [.0038]
    # coupon: coupon rate
    # init_price: the bond price observed from market. Set to 0 can compute the theoretical price of the bond
    rate_before.extend(rate)
    r = rate_before
    discount_low = discount_factor(r)
    discount_high = discount_factor(np.multiply(r, np.exp(2*sigma)))
    cash_coupon = coupon * par
    price = (probability*(cash_coupon*sum(discount_low[:-1]) + (cash_coupon+par) / discount_low[-1])
             + (1 - probability) * (cash_coupon*sum(discount_high[:-1])
                                    + (cash_coupon+par) / discount_high[-1])) - init_price
    return price


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
    implied_forward_rate = []
    # get discount for every interval
    discounts = []
    for k, v in discount_set.items():
        if k % interval == 0:
            discounts.append(discount_set[k])
    for i, v in enumerate(discounts):
        if i+1 < len(discounts):
            implied_forward_rate.append(discounts[i]/discounts[i+1]-1)
    implied_forward_rate.insert(0, 1 / discount_set[interval] - 1)
    tree = [1 / discount_set[interval] - 1]
    for ind, val in enumerate(implied_forward_rate[:-1]):
        bond = zb_price[interval + interval * (ind + 1)]
        params = (implied_forward_rate[:ind+1], bond['coupon'], bond['price'], sigma)
        cal_rate = optimize.fsolve(bond_value, implied_forward_rate[ind+1], args=params)
        tree.append(list(cal_rate))
    for i, v in enumerate(tree[1:]):
        k = 1
        while k < i + 2:
            tree[i + 1].append(tree[i + 1][k - 1] * 1.2712)
            k += 1
    return tree
