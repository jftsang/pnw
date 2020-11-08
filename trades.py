#!/usr/bin/env python3
import argparse
import datetime
from dateutil.relativedelta import relativedelta
import io
import json
import logging
import os
import time
import matplotlib.dates as mdates
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from config import *

TRADE_HISTORY = "tradehistory.csv"

def get_new_trades():
    api_return = api_call("trade-history")
    new_trades = pd.read_json(io.StringIO(json.dumps(api_return['trades'])),
                          dtype={'volume': np.int64, 'price': np.int64})
    return new_trades


def update_trade_history():
    new_trades = get_new_trades()
    if os.path.isfile(TRADE_HISTORY):
        trade_history = pd.read_csv(TRADE_HISTORY,
                                    index_col=0,
                                    parse_dates=['date'],
                                    dtype={'volume': np.int64,
                                           'price': np.int64})
        trade_history = trade_history.append(new_trades).drop_duplicates()
    else:
        trade_history = new_trades

    trade_history = trade_history.sort_values('date')
    trade_history.to_csv(TRADE_HISTORY)
    return trade_history, new_trades


def get_current_prices(resource):
    logging.info(f"Getting prices for {resource}...")
    traceprice_url = f"http://politicsandwar.com/api/tradeprice/?resource={resource}&key={API_KEY}"
    res = requests.get(url=traceprice_url).json()
    res['avgprice'] = int(res['avgprice'])
    res['highestbuy']['price'] = int(res['highestbuy']['price'])
    res['lowestbuy']['price'] = int(res['lowestbuy']['price'])
    return res


def makeplot(trades, resource, ax=plt.gca()):
    trades = trades[trades.resource == resource]
    trades = trades.sort_values('date')

    trades = trades[trades.date >=  datetime.datetime.now() + relativedelta(days=-1)]
    sells = trades[trades.offer_type == 'sell']
    buys = trades[trades.offer_type == 'buy']

    current_prices = get_current_prices(resource)

    # breakpoint()
    ax.plot(buys.date, buys.price, 'bx',
            [pd.Timestamp(current_prices['highestbuy']['date'])],
            [current_prices['highestbuy']['price']],
            'bo',
            sells.date, sells.price, 'r+',
            [pd.Timestamp(current_prices['lowestbuy']['date'])],
            [current_prices['lowestbuy']['price']],
            'ro')

    plt.legend(['buys', 'highest buy offer',
                'sells', 'lowest sell offer'])

    # days = mdates.DayLocator()
    hours = mdates.HourLocator(range(0,24,2))
    hours_fmt = mdates.DateFormatter('%H')

#    ax.xaxis.set_major_locator(days)
#    ax.xaxis.set_minor_locator(hours)
    ax.xaxis.set_major_locator(hours)
    ax.xaxis.set_major_formatter(hours_fmt)
    ax.set(title=resource,
           ylim=[
            min(trades.price.quantile(0.2),
                current_prices['highestbuy']['price'])*0.95,
            max(trades.price.quantile(0.8),
                current_prices['lowestbuy']['price'])*1.05
        ])
    ax.grid()


def main(args):
    resources = [["credits", "coal", "oil", "uranium"],
                 ["lead", "iron", "bauxite", "gasoline"],
                 ["munitions", "steel", "aluminum", "food"]]
    while True:
        trade_history, new_trades = update_trade_history()
        #resources = [["coal", "oil", "iron"],
        #             ["gasoline", "steel", "food"]]
        fig, axs = plt.subplots(3, 4, figsize=(16, 10))
        for i in range(3):
            for j in range(4):
                makeplot(trade_history, resources[i][j], axs[i][j])
        plt.figure(fig.number)
        plt.savefig('tradehist.png')
        # plt.show()
        logging.info(f"Sleeping for {SLEEP_TIME}...")
        time.sleep(SLEEP_TIME)


    # makeplot(args.resource)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument("resource")
    args = parser.parse_args()
    main(args)

