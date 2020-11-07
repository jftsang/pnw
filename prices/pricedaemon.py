#!/usr/bin/env python3
import time
from prices import update_price_history
import subprocess
from requests.exceptions import ConnectionError, Timeout
import matplotlib.pyplot as plt
import pandas as pd
from config import *

count = 0
resources = ["coal", "oil", "iron", "steel", "gasoline"]

def daemon():
    while True:
        try:
            for r in resources:
                update_price_history(r)
                subprocess.run(["gnuplot", "-e", f"resource='{r}'", "pricehist.gnuplot"])
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            print("Couldn't update.")

        print("Waiting...")
        time.sleep(SLEEP_TIME)
        count += 1


def plot_prices(resource):
    history = pd.read_csv(f"{resource}.csv")
    breakpoint()
    plt.plot(history)
    outfile = "{resource}-new.png"
    plt.savefig(outfile)

