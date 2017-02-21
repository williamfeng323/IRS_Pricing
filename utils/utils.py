import urllib.request as request
import urllib.parse
from bs4 import BeautifulSoup
import re


def get_libor(content):
    tr_list = content.find('div', class_='boxcontent').findAll('tr')
    libor = {}
    for tr in tr_list[3:5]:
        period_reg = re.compile('(\d+)\s')
        libor['period'] = period_reg.match(tr.find('strong').string).group(1)
        libor['rate'] = float(tr.find_all('td')[1].string)
    return libor


def get_spotcurve(content):
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


def get_treasury_price(content):
    # Use mock data for development first
    return {.25: {'price': 99.862000, 'coupon': 0}, .5: {'price': 99.664500, 'coupon': 0},
            .75: {'price': 99.436333, 'coupon': 0}, 1: {'price': 99.193056, 'coupon': 0},
            1.25: {'price': 103.56250, 'coupon': 0.03875}, 1.5: {'price': 104.312500, 'coupon': 0.04},
            1.75: {'price': 100.062500, 'coupon': 0.01250}, 2: {'price': 102.875000, 'coupon': 0.02750},
            2.25: {'price': 103.843750, 'coupon': 0.03125}, 2.5: {'price': 105.343750, 'coupon': 0.03625},
            2.75: {'price': 105.062500, 'coupon': 0.03375}, 3: {'price': 106.000000, 'coupon': 0.03625},
            }


def get_rawdata(category, specific_url=None):
    # url parameters
    categories = {'LIBOR': {'url':'http://www.bankrate.com/rates/interest-rates/libor.aspx'},
             'SPOTCURVE': {'url':'https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=yield'},
             'TREASURY_PRICE': {'url': 'https://www.treasurydirect.gov/GA-FI/FedInvest/selectSecurityPriceDate.htm',
                               'parm': {'priceData.month': '1', 'priceData.day': '1', 'priceData.year': '2017', 'submit': 'Show+Prices'}}
                  }
    # send http request to retrieve page
    if specific_url is None:
        url = categories[category.upper()]['url']
    # if 'parm' in categories[category.upper()]:
    #     params = bytes(urllib.parse.urlencode(categories[category.upper()]['parm']).encode())
    #     page = request.urlopen(url, params)
    # else:
    #     page = request.urlopen(url)
    # page = BeautifulSoup(page, 'lxml')
    page = None
    return {
        'LIBOR': lambda content: get_libor(content),
        'YIELD_CURVE': lambda content: get_spotcurve(content),
        'TREASURY_PRICE': lambda content: get_treasury_price(content)
    }[category.upper()](page)


