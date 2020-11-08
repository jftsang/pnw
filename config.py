import logging
import requests
import time

logging.getLogger().setLevel(logging.INFO)

API_PATH = "https://politicsandwar.com/api"
API_KEY = "CHANGEME"

SLEEP_TIME = 1200


SMTP_SERVER = "example.com"
SMTP_PORT = 587  # For starttls
SMTP_EMAIL = "you@example.com"
SMTP_PASSWORD = "your_password"

def Timed(f):
    def timed(*args, **kwargs):
        logging.info(f"Tic.")
        tic = time.time()
        return_value = f(*args, **kwargs)
        toc = time.time()
        logging.info(f"Toc. {toc - tic}s.")
        return return_value

    return timed


class UnsuccessfulAPIError(Exception):
    pass
    # https://stackoverflow.com/questions/1319615/proper-way-to-declare-custom-exceptions-in-modern-python
#    def __init__(self, message, errors):
#        super().__init__(message)
#
#        self.errors = errors

@Timed
def api_call(category, key=API_KEY):
    api_url = f"{API_PATH}/{category}/?key={key}"
    logging.info(f"Making API call to {api_url}...")
    r = requests.get(url=api_url).json()
    if not r['success']:
        raise UnsuccessfulAPIError
    return r
