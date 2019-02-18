#!/usr/bin/env python3

import requests
import json
import os
import csv
import collections
import time
from datetime import datetime, timedelta

HISTORICAL_URL = 'https://api.coindesk.com/v1/bpi/historical/close.json?start=<VALUE>&end=<VALUE>'
CURRENT_URL = 'https://api.coindesk.com/v1/bpi/currentprice.json'
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))

"""
Saves historical Bitcoin Price Index (BPI) values to CSV file.
Params:
    index: counter currency of base/counter pair (e.g. USD in BTC/USD).
    currency: what currency price is displayed in (e.g. BPI for BTC/CNY in USD).
    start: starting date to get BPI for.
    end: last date to get BPI for. NOTE: if end date is current date, Coindesk will not have BPI calculated yet.
        Effective end date becomes yesterday's date.
    file_name: file to write to in current directory.
    write_mode: mode to open file in. Default mode creates/overwrites file.
"""
def get_historical_json(index=None, currency=None, start=None, end=None, file_name='bpi_data.csv', write_mode='w'):
    payload = {}
    if start:
        assert (end)
        payload['start'] = start
        payload['end'] = end
    if index: payload['index'] = index
    if currency: payload['currency'] = currency

    r = requests.get(HISTORICAL_URL, params=payload)
    print('Request made to: {}'.format(r.url))

    ordered_data_dict = json.JSONDecoder(object_pairs_hook=collections.OrderedDict).decode(r.text)['bpi']

    # CSV file location
    csv_file_path = os.path.join(ROOT_DIR, file_name)

    with open(csv_file_path, write_mode) as csv_file:
        csv_writer = csv.writer(csv_file, delimiter=',')

        #if this is a fresh file, write index/currency as first line
        if not index: index = 'USD'
        if not currency: currency = 'USD'
        if write_mode == 'w': csv_writer.writerow([index, currency])
        for date in ordered_data_dict:
            csv_writer.writerow([date, ordered_data_dict[date]])

    return file_name

"""
Gets all BPI info from specified start date to today. Default generated file name specifies date range.
Params:
    start: starting date to get BPI for. Default value is earliest available date.
    index: counter currency of base/counter pair (e.g. USD in BTC/USD).
    currency: what currency price is displayed in (e.g. BPI for BTC/CNY in USD).
"""

def get_all_bpi(start = datetime.strftime(datetime.now() - timedelta(5), '%Y-%m-%d'), index='Date', currency='USD'):
    end = time.strftime('%Y-%m-%d')
    print('Today\'s date: {}'.format(end))
    get_historical_json(index=index, currency=currency, start=start, end=end, file_name='last_five_days.csv')


"""
Gets parameters from old BPI file so new request can be generated for update.
"""
def get_old_params(csv_filename):
    with open(csv_filename, 'r') as f:
        csv_reader = csv.reader(f)
        firstrow = next(csv_reader)
        lastrow = collections.deque(csv.reader(f), 1)[0]
        return (firstrow,lastrow)

"""
Updates existing data file current price history. Assumes file is in same directory as script. If run on already up to
    date file, will append extra line to file (yesterday's date), so only run once.
"""
def update_existing_bpi(dated_file_name):
    #change this to use some other file location logic
    dated_file_path = os.path.join(ROOT_DIR, dated_file_name)

    params, last_date_info = get_old_params(dated_file_path)
    index = params[0]
    currency = params[1]
    start = last_date_info[0]
    end = time.strftime('%Y-%m-%d')
    get_historical_json(index=index, currency=currency, start=start, end=end, file_name=dated_file_name, write_mode='a')

"""
Gets current BPI ticker and converts to streamlined dict.
Params:
    currency_code: optional param to specify which currency BPI you want.
Returns:
    Dictionary clean_dict:
        'timestamp':string iso-format timestamp.
        'bpi': dict of currency code to price.
"""
def get_current_price(currency_code=None):
    url_to_request = CURRENT_URL
    if currency_code: url_to_request = 'https://api.coindesk.com/v1/bpi/currentprice/{}.json'.format(currency_code)
    print(url_to_request)
    r = requests.get(url_to_request)
    r_as_dict = r.json()

    timestamp = r_as_dict['time']['updatedISO']
    bpi = {}
    for currency in r_as_dict['bpi']:
        bpi[currency] = r_as_dict['bpi'][currency]['rate_float']

    clean_dict = {}
    clean_dict['timestamp'] = timestamp
    clean_dict['bpi'] = bpi

    return clean_dict

"""
Default main just generates file of all BPI history and prints current BPI.
"""
if __name__ == '__main__':
    get_all_bpi()
    print(get_current_price('CNY'))
