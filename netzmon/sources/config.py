import csv
import logging
import time

TIMESTAMP = 0
MODEM_LOGIN_POST_URL = "http://192.168.1.1/goform/login"
MODEM_STATUS_PAGE_URL = "http://192.168.1.1/RgConnect.asp"
MODEM_LOGOUT_URL = "http://192.168.1.1/logout.asp"
MODEM_LOGIN_USERNAME_KEY = 'loginUsername'
MODEM_LOGIN_USERNAME_VALUE = ""
MODEM_LOGIN_PASSWORD_KEY = 'loginPassword'
MODEM_LOGIN_PASSWORD_VALUE = ""
ROUTER_IP = '192.168.2.1'
MODEM_IP = '192.168.1.1'
ISR_DNS_IP = '31.168.224.100'
GOOGLE_DNS_IP = '8.8.8.8'
# TODO access key loading from csv
JSON_RAW_FEED_DIRECTORY_PATH = "../resources/json/raw feed"
JSON_DAILY_FEED_DIRECTORY_PATH = "../resources/json/daily feed"
LOGGING_LEVEL = logging.DEBUG
AWS_CREDENTIALS_FILE = "../recources/aws/credentials.csv"
AWS_KEYSTORE = {}


def timestamp():
    global TIMESTAMP
    if TIMESTAMP == 0:
        TIMESTAMP = int(time.time())

    return TIMESTAMP


# Singleton pattern - lazy instantiation
def get_aws_secret_from_csv():
    global AWS_KEYSTORE
    if len(AWS_KEYSTORE) == 0:
        with open(AWS_CREDENTIALS_FILE, mode='r') as csv_file:
            csv_reader = csv.DictReader(csv_file)
            AWS_KEYSTORE = csv_reader

    return  AWS_KEYSTORE


def setup_logging():
    # Set up logging
    logging.basicConfig(level=LOGGING_LEVEL,
                        format='%(levelname)s: %(asctime)s: %(message)s')
