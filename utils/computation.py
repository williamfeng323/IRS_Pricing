import numpy as np
from scipy import optimize
import matplotlib.pyplot as plt
import utils.utils as util
import utils.bin_tree as btree


def zb_discount(curve='TREASURY_PRICE', maturity=None, interval=.5):
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
    return value_tree


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
    return back_count(r, coupon, interval)[-1][0] - init_price


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
        cal_rate = optimize.fsolve(bond_value, implied_forward_rate[ind+1], args=params)
        nodes = [float(cal_rate)]
        i = 0
        while i < len(tree):
            nodes.append(nodes[i] * np.exp(sigma * 2))
            i += 1
        tree.append(nodes)
    return tree


def draw_tree(raw_tree):
    my_tree = list()
    init_nodes = list()
    for v in raw_tree[-1]:
        init_nodes.append(btree.Node(v))
    my_tree.append(init_nodes)
    i = 0
    while i < len(raw_tree) - 1:
        temp = list()
        last_nodes = my_tree[-1]
        root = raw_tree[-2 - i]
        for k, v in enumerate(root):
            node = btree.Node(root[k])
            node.l = last_nodes[k]
            node.r = last_nodes[k+1]
            temp.append(node)
        my_tree.append(temp)
        i += 1
    return btree.Tree(my_tree[-1][0])


def calculate_bond(coupon, par, maturity, interval=.5):
    rate_tree = calibrate_tree(interval)
    price = back_count(rate_tree, coupon, interval, par, maturity)[-1][0]
    return price


def calculate_swap_exposures(coupon, pay_flag=-1, probability=.5, interval=.5):
    rates = calibrate_tree(interval)
    payoff = list()
    import pdb
    for v in rates:
        payoff.append(np.add(pay_flag * coupon * interval, v).tolist())
        # pdb.set_trace()
        payoff[-1] = [100*x for x in payoff[-1]]
    values = [payoff[-1]]
    values.append((np.array(values[0])/(1+np.array(rates[-1]))).tolist())
    for ind, val in enumerate(rates):
        nodes = list()
        last_rate = rates[-1 - ind]
        end_value = values[-1]
        for i, v in enumerate(end_value):
            # pdb.set_trace()
            if i < len(end_value) - 1:
                exp_v = expected_value(last_rate[i], end_value[i], end_value[i + 1], probability)
                nodes.append(exp_v)
        if len(last_rate) != 1:
            values.append(np.add(nodes, payoff[-2 - ind]).tolist())
    swap_value = values[-1][0]
    payoff_tree = draw_tree(payoff)
    values = list(reversed(values[1:]))
    value_tree = draw_tree(values)
    exposures = list()
    for ind, val in enumerate(values[1:]):
        exposure = 0.0
        for v in val:
            exposure += max(0, v) * np.power(probability, len(val)) * len(value_tree.binaryTreePaths(v))
        for v in payoff[ind]:
            exposure += max(0, v) * np.power(probability, len(payoff[ind])) * len(payoff_tree.binaryTreePaths(v))
        exposures.append(exposure)
    last_exposure = 0.0
    for v in payoff[-1]:
        last_exposure += max(0, v) * np.power(probability, len(payoff[-1])) * len(payoff_tree.binaryTreePaths(v))
    exposures.append(last_exposure)
    return exposures, swap_value


def calculate_swap(fixed_rate, maturity, interval=.5, pay_flag=-1, counterparty='boa', self_symbol='citi',
                   cp_loss_severity=.4, self_loss_severity=.4):
    zb_price, discount_set = zb_discount('TREASURY_PRICE', interval)
    cva_exposures, swap_value = calculate_swap_exposures(fixed_rate,pay_flag)
    dva_exposures, c_swap_value = calculate_swap_exposures(fixed_rate, -1*pay_flag)
    discounts = list()
    for k, v in discount_set.items():
        if k % interval == 0:
            discounts.append(discount_set[k])
    hazard_rate = util.get_hazard_rate(maturity, interval)
    cva = sum(np.array(cva_exposures) *
              np.array(discounts) * np.array(list(hazard_rate[counterparty].values())) * cp_loss_severity)
    dva = sum(np.array(dva_exposures) *
              np.array(discounts) * np.array(list(hazard_rate[self_symbol].values())) * self_loss_severity)
    print('Value of swap assume no default: ' + str(swap_value))
    print('Value of CVA: ' + str(cva))
    print('Value of DVA: ' + str(dva))
    return swap_value - cva + dva






