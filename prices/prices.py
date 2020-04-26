#!/usr/bin/env python3

import requests
from pprint import pprint
import os
import time
import logging
logging.getLogger().setLevel(logging.INFO)

from config import API_KEY
# or...
# API_KEY = "your_api_key"

def get_spread(resource):
    logging.info(f"Getting prices for {resource}...")
    traceprice_url = f"http://politicsandwar.com/api/tradeprice/?resource={resource}&key={API_KEY}"
    r = requests.get(url=traceprice_url).json()
    return (r["highestbuy"]["price"], r["highestbuy"]["amount"],
            r["avgprice"],
            r["lowestbuy"]["price"], r["lowestbuy"]["amount"])


def update_price_history(resource, histfile=None):
    if histfile is None:
        histfile = f"{resource}.csv"

    timestr = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
    highbuy, highbuyq, avgprice, lowsell, lowsellq = get_spread(resource)

    if not os.path.isfile(histfile):
        with open(histfile, "a") as f:
            f.write(f"datetime,highbuy,highbuyq,avgprice,lowsell,lowsellq\n")


    with open(histfile, "a") as f:
        f.write(f"{timestr},{highbuy},{highbuyq},{avgprice},{lowsell},{lowsellq}\n")


if __name__ == "__main__":
    update_price_history("steel")
    update_price_history("gasoline")
