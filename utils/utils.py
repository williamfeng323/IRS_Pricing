import urllib.request as request
import urllib.parse
from bs4 import BeautifulSoup
import re
import datetime
from dateutil.relativedelta import *
from scipy import interpolate
import numpy as np
import matplotlib.pyplot as plt


def get_libor(content, interval=None):
    tr_list = content.find('div', class_='boxcontent').findAll('tr')
    libor = {}
    for tr in tr_list[3:5]:
        period_reg = re.compile('(\d+)\s')
        libor['period'] = period_reg.match(tr.find('strong').string).group(1)
        libor['rate'] = float(tr.find_all('td')[1].string)
    return libor


def interpolating(init_point, maturity, interval):
    tck = interpolate.splrep(list(init_point.keys()), list(init_point.values()), k=3)
    newx = np.arange(interval, maturity + interval, interval)
    newy = interpolate.splev(newx, tck, der=0)
    plt.plot(list(init_point.keys()), list(init_point.values()), 'o', newx, newy, 'r.-')
    plt.legend(['Observed', 'cubic spline'], loc='best')
    plt.show()
    return dict(zip(newx.tolist(), newy.tolist()))


def get_hazard_rate(maturity, interval):
    if maturity > 5:
        maturity = 5
    boa_observed_hazard_rate = {.25: .0003, .5: .0012, .75: .0045, 1: .0149, 2: .1675, 3: .5043, 4: 1.1416, 5: 1.8261}
    citi_observed_hazard_rate = {.25: .0008, .5: .0032, .75: .0115, 1: .0338, 2: .2716, 3: .6936, 4: 1.4888, 5: 2.2835}
    boa_hazard_rate = interpolating(boa_observed_hazard_rate, maturity, interval)
    citi_hazard_rate = interpolating(citi_observed_hazard_rate, maturity, interval)
    return {'boa': boa_hazard_rate, 'citi': citi_hazard_rate}


def get_ytmcurve(content, interval=None):
    spotcurve = {}
    header = content.find('table', class_='t-chart').findAll('th')[1:]
    period_rule = re.compile('(\d+)\s([a-z]{2})')
    # set period
    for val in header:
        period = period_rule.match(val.string)
        if period.group(2) == 'mo':
            spotcurve[float(period.group(1)) / 12] = 0
        else:
            spotcurve[float(period.group(1))] = 0
    raw_curve = content.find('table', class_='t-chart').findAll('tr')[-1].findAll('td')[1:]
    # set rate for each period
    i = 0
    for key, val in spotcurve.items():
        spotcurve[key] = float(raw_curve[i].string)
        i += 1


def get_treasury_price(content, maturity=5, interval=.5):
    tr_list = content.find('table', class_='data1').findAll('tr')[1:]
    bond_list = dict.fromkeys(np.arange(interval, maturity + interval, interval).tolist())
    today = datetime.date.today()
    for v in tr_list:
        info = v.findAll('td')
        bond_maturity = datetime.datetime.strptime(info[3].string, '%m/%d/%Y').date()
        bond_maturity_in_years = (bond_maturity - today).days / 365
        for k in bond_list.keys():
            if k*.90 < bond_maturity_in_years < k*1.10 and\
                    (info[1].string != 'TIPS' and info[1].string != 'MARKET BASED FRN'):
                diff = abs(bond_maturity_in_years - k)
                if bond_list[k] is None or (abs(bond_list[k]['bond_maturity_in_years'] - k)) > diff:
                    bond_list[k] = {'price': float(info[6].string),
                                    'coupon': float(info[2].string.strip('%'))/100,
                                    'bond_maturity_in_years': bond_maturity_in_years
                                    }
    return bond_list


def get_rawdata(category, maturity, interval, specific_url=None, data_date=None):
    # url parameters
    categories = {'LIBOR': {'url':'http://www.bankrate.com/rates/interest-rates/libor.aspx'},
             'YTMCURVE': {'url':'https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=yield'},
             'TREASURY_PRICE': {'url': 'https://www.treasurydirect.gov/GA-FI/FedInvest/selectSecurityPriceDate.htm',
                               'parm': {
                                   'priceData.month': '1',
                                   'priceData.day': '1',
                                   'priceData.year': '2017',
                                   'submit': 'Show+Prices'
                                    }
                                }
                  }
    # send http request to retrieve page
    if specific_url is None:
        url = categories[category.upper()]['url']
    if data_date is None:
        data_date = datetime.date.today()-relativedelta(days=+1)
    if 'parm' in categories[category.upper()]:
        params = categories[category.upper()]['parm']
        params['priceData.month'] = data_date.month
        params['priceData.year'] = data_date.year
        params['priceData.day'] = data_date.day
        params = bytes(urllib.parse.urlencode(params).encode())
        page = request.urlopen(url, params)
    else:
        page = request.urlopen(url)
    page = BeautifulSoup(page, 'lxml')
    return {
        'LIBOR': lambda content: get_libor(content),
        'YTMCURVE': lambda content: get_ytmcurve(content),
        'TREASURY_PRICE': lambda content, m, i: get_treasury_price(content, m, i)
    }[category.upper()](page, maturity, interval)


