#!/usr/bin/env python3
import time
from prices import update_price_history
import subprocess
from requests.exceptions import ConnectionError, Timeout

count = 0
resources = ["steel", "gasoline"]
while count < 48 * 14:
    try:
        for r in resources:
            update_price_history(r)
            subprocess.run(["gnuplot", "-e", f"resource='{r}'", "pricehist.gnuplot"])
    except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
        print("Couldn't update.")

    print("Waiting...")
    time.sleep(1800)
    count += 1
