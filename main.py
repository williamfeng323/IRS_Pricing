import utils.computation as cp
tree = cp.draw_tree(cp.calibrate_tree())
tree.binaryTreePaths(0.0080876771453680923)
vt = cp.calculate_swap_exposures(.04)


import urllib.request as request
import urllib.parse
from bs4 import BeautifulSoup
import utils.util as ut
import datetime
categories = {'LIBOR': {'url':'http://www.bankrate.com/rates/interest-rates/libor.aspx'},
         'YTMCURVE': {'url':'https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=yield'},
         'TREASURY_PRICE': {'url': 'https://www.treasurydirect.gov/GA-FI/FedInvest/selectSecurityPriceDate.htm',
                           'parm': {'priceData.month': '1', 'priceData.day': '1', 'priceData.year': '2017', 'submit': 'Show+Prices'}}
              }
category = 'TREASURY_PRICE'
url = categories[category.upper()]['url']
if 'parm' in categories[category.upper()]:
    params = categories[category.upper()]['parm']
    params['priceData.month'] = datetime.date.today().month
    params['priceData.year'] = datetime.date.today().year
    params['priceData.day'] = datetime.date.today().day
    params = bytes(urllib.parse.urlencode(params).encode())
    page = request.urlopen(url, params)
else:
    page = request.urlopen(url)
page = BeautifulSoup(page, 'lxml')
# ut.get_treasury_price(page, 5, .5)