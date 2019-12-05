import json
import logging
import os
import pingparsing
from humanreadable import ParameterError
from pingparsing import ParseError
from netzmon.sources import config


# Pingparser usage doc: https://pingparsing.readthedocs.io
def pingparse(ip):
    ping_parser = pingparsing.PingParsing()
    transmitter = pingparsing.PingTransmitter()
    transmitter.destination = ip
    transmitter.count = 5
    result = transmitter.ping()
    return ping_parser.parse(result).as_dict()


def generate_connectivity_test():
    logging.info("Connectivity test started.")
    ips = {'router_ip': config.ROUTER_IP, 'modem_ip': config.MODEM_IP,
           'isr_dns': config.ISR_DNS_IP, 'google_dns': config.GOOGLE_DNS_IP}
    result_list = []
    timestamp = config.timestamp()

    for ip_key in ips.keys():
        logging.info("Testing connectivity for destination: %", ips[ip_key])
        try:
            result = {'host': ip_key, 'timestamp': timestamp, 'ping result': pingparse(ips[ip_key])}
        except (ParseError, ValueError, ParameterError) as e:
            logging.error(e)
        result_list.append(result)

    directory_name = config.JSON_RAW_FEED_DIRECTORY_PATH
    filename = "connectivity-check-" + str(timestamp) + ".json"
    try:
        os.makedirs(directory_name, exist_ok=True)
        with open(directory_name + "/" + filename, 'w', encoding='utf-8') as f:
            json.dump(result_list, f, ensure_ascii=False, indent=4)
    except OSError as e:
        logging.error(e)
    logging.info("Connectivity check results successfully written to following JSON file: %", filename)
