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
import plotly.express as px
import plotly.graph_objects as go
import psutil

from config import *


TRADE_HISTORY = "tradehistory.csv"
OUTDIR = os.path.join(os.getcwd(), "graphs")
os.makedirs(OUTDIR, exist_ok=True)

def get_new_trades():
    api_return = api_call("trade-history")
    new_trades = pd.read_json(io.StringIO(json.dumps(api_return['trades'])),
                          dtype={'volume': np.int64, 'price': np.int64})
    return new_trades


def get_trade_history(update=True):
    if update:
        new_trades = get_new_trades()
    if os.path.isfile(TRADE_HISTORY):
        trade_history = pd.read_csv(TRADE_HISTORY,
                                    index_col=0,
                                    parse_dates=['date'],
                                    dtype={'volume': np.int64,
                                           'price': np.int64})
        if update:
            trade_history = trade_history.append(new_trades).drop_duplicates()
    else:
        if update:
            trade_history = new_trades
        else:
            raise FileNotFoundError

    trade_history = trade_history.sort_values('date')
    trade_history.to_csv(TRADE_HISTORY)
    return trade_history


def get_current_prices(resource):
#    res = {'avgprice': 2,
#           'highestbuy': {'price': 1, 'date': '2020-11-13 02:59:27'},
#           'lowestbuy': {'price': 3, 'date': '2020-11-13 02:59:27'}}
    logging.info(f"Getting current price and offers for {resource}...")
    traceprice_url = f"http://politicsandwar.com/api/tradeprice/?resource={resource}&key={API_KEY}"
    res = requests.get(url=traceprice_url).json()
    res['avgprice'] = int(res['avgprice'])
    res['highestbuy']['price'] = int(res['highestbuy']['price'])
    res['lowestbuy']['price'] = int(res['lowestbuy']['price'])
    return res


def makeplot(trades, current_prices, resource, ax=plt.gca()):
    trades = trades[trades.resource == resource]
    trades = trades.sort_values('date')

    trades = trades[trades.date >=  datetime.datetime.now() + relativedelta(days=-1)]
    sells = trades[trades.offer_type == 'sell']
    buys = trades[trades.offer_type == 'buy']

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
    ax.grid(True)


def plotly(trades, current_prices, resource):
    trades = trades[trades.resource == resource]
    trades = trades[trades.date >= datetime.datetime.now() + relativedelta(days=-1)]
    trades['logquantity'] = np.log2(trades.quantity)
    sells = trades[trades.offer_type == 'sell']
    buys = trades[trades.offer_type == 'buy']

    fig = px.scatter(trades,
            x="date",
            y="price",
            color="offer_type",
            size="logquantity",
            hover_data=["quantity"],
            color_discrete_map={'buy': 'blue', 'sell': 'red'}
            )
    fig.add_trace(go.Scatter(
        name="lowest sell offer",
        x=[current_prices['lowestbuy']['date']],
        y=[current_prices['lowestbuy']['price']],
        mode="markers",
        marker={'color': 'red', 'symbol': 'x'}
        ))
    fig.add_trace(go.Scatter(
        name="highest buy offer",
        x=[current_prices['highestbuy']['date']],
        y=[current_prices['highestbuy']['price']],
        mode="markers",
        marker={'color': 'blue', 'symbol': 'cross'}
        ))
    ymin = min(trades.price.quantile(0.2),
               current_prices['highestbuy']['price'])*0.95
    ymax = max(trades.price.quantile(0.8),
               current_prices['lowestbuy']['price'])*1.05
    fig.update_layout(
        title=resource,
        autosize=False, width=800, height=600,
        margin=dict(l=50, r=50, b=100, t=100, pad=4),
        showlegend=True,
        paper_bgcolor="LightSteelBlue")
    fig.update_xaxes(title_text="date", dtick=7200000)
    fig.update_yaxes(title_text="price", range=[ymin, ymax])
    fig.write_html(os.path.join(OUTDIR, f"plotly-{resource}.html"),
                   include_plotlyjs="cdn")


def main(args):
    resources = ["credits", "coal", "oil", "uranium",
                 "lead", "iron", "bauxite", "gasoline",
                 "munitions", "steel", "aluminum", "food"]
    while True:
        try:
            trade_history = get_trade_history()
        except Exception as e:
            logging.exception(e)
            continue

        fig_multi, axs = plt.subplots(3, 4, figsize=(18, 14))
        for ind in range(len(resources)):
            resource = resources[ind]
            fig_single = plt.figure(ind)
            ax = fig_single.gca()

            try:
                current_prices = get_current_prices(resource)
                makeplot(trade_history, current_prices, resource, ax)
                fig_single.savefig(os.path.join(OUTDIR, f'tradehist-{resource}.png'))
                plotly(trade_history, current_prices, resource)

                plt.figure(fig_multi.number)
                i, j = ind // 4, ind % 4
                makeplot(trade_history, current_prices, resource, axs[i][j])
            except Exception as e:
                logging.exception(e)
                continue

        fig_multi.savefig(os.path.join(OUTDIR, 'tradehist-all.png'))
        process = psutil.Process(os.getpid())
        print(process.memory_info().vms / 1e6)  # megabytes
        print(process.memory_info().rss / 1e6)

        logging.info(f"Sleeping for {SLEEP_TIME}...")
        try:
            time.sleep(SLEEP_TIME)
        except KeyboardInterrupt:
            input('Enter to refresh, or Ctrl-C again to quit')
            continue


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # parser.add_argument("resource")
    args = parser.parse_args()
    main(args)
