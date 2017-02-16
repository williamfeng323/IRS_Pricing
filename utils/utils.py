import urllib.request as request
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
    for k, val in spotcurve.items():
        spotcurve[k] = raw_curve[i].string
        i += 1
    return spotcurve


def get_rawdata(category, specific_url=None):
    categories = {'LIBOR':'http://www.bankrate.com/rates/interest-rates/libor.aspx',
             'SPOTCURVE':'https://www.treasury.gov/resource-center/data-chart-center/interest-rates/Pages/TextView.aspx?data=yield'}
    if specific_url is None:
        url = categories[category.upper()]
    page = request.urlopen(url)
    page = BeautifulSoup(page, 'lxml')
    return {
        'LIBOR': lambda content: get_libor(content),
        'SPOTCURVE': lambda content: get_spotcurve(content)
    }[category.upper()](page)




