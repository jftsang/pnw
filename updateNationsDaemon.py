#!/usr/bin/env python3
"""A daemon that periodically updates the list of nations stored locally.
"""
import json
import logging
logging.getLogger().setLevel(logging.INFO)
import time

import requests
from requests.exceptions import ConnectionError, Timeout

from config import API_KEY, API_PATH, SLEEP_TIME

def update_nation_list(fn="nations.txt"):
    logging.info("Getting new list of nations...")

    tic = time.time()
    api_url = f"{API_PATH}/nations/?key={API_KEY}"
    r = requests.get(url=api_url).json()
    if not r["success"]:
        raise UnsuccessfulAPIError("failed to update list of nations")

    with open(fn, "w") as fp:
        json.dump(r, fp)

    toc = time.time()
    logging.info(f"Successfully updated the list of nations. ({toc - tic}s)")


class UnsuccessfulAPIError(Exception):
    pass
    # https://stackoverflow.com/questions/1319615/proper-way-to-declare-custom-exceptions-in-modern-python
#    def __init__(self, message, errors):
#        super().__init__(message)
#
#        self.errors = errors


def daemon():
    while True:
        try:
            update_nation_list()
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
            print("Couldn't update.")
        except UnsuccessfulAPIError as e:
            logging.exception(e)

        print("Waiting...")
        time.sleep(SLEEP_TIME)

if __name__ == "__main__":
    update_nation_list()
    # daemon()
