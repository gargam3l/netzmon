import json
import logging
import os
from json import JSONDecodeError

import boto3 as boto3

if __package__ is None or __package__ == '':
    # uses current directory visibility
    import config
else:
    # uses current package visibility
    from netzmon.sources import config


def upload_single_file_to_s3(filename, path):
    bucket_name = "netzmon"
    filename_with_path = path + "/" + filename
    # AWS_ACCESS_KEY_ID = config.AWS_ACCESS_KEY_ID
    # AWS_SECRET_ACCESS_KEY = config.AWS_SECRET_ACCESS_KEY
    aws_access_key_id = config.get_aws_secret_from_csv()["Access key ID"]
    aws_secret_access_key = config.get_aws_secret_from_csv()["Secret access key"]
    s3 = boto3.resource(service_name='s3', aws_access_key_id=aws_access_key_id,
                        aws_secret_access_key=aws_secret_access_key)
    s3.meta.client.upload_file(Filename=filename_with_path, Bucket=bucket_name, Key=filename)


def upload_daily_feed_to_s3():
    pending_dir = config.JSON_DAILY_FEED_DIRECTORY_PATH + "/pending"
    processed_dir = config.JSON_DAILY_FEED_DIRECTORY_PATH + "/processed"
    daily_feed_json_file_list = os.listdir(pending_dir)
    for f in daily_feed_json_file_list:
        upload_single_file_to_s3(f, pending_dir)
        move_file(f, pending_dir, processed_dir)


def merge_raw_feed_json_files_to_daily_feed_json():
    timestamp_now = config.timestamp()
    timestamp_minus_24hrs = timestamp_now - 24 * 60 * 60
    raw_feed_json_file_list = os.listdir(config.JSON_RAW_FEED_DIRECTORY_PATH)
    raw_feed_connectivity_check_list = []
    raw_feed_modem_status_list = []
    for file in raw_feed_json_file_list:
        file_timestamp = int(file[file.rfind("-") + 1: file.find(".")])
        if file_timestamp < timestamp_minus_24hrs:
            if len(file) == 34:
                raw_feed_connectivity_check_list.append(config.JSON_RAW_FEED_DIRECTORY_PATH + "/" + file)
            elif len(file) == 28:
                raw_feed_modem_status_list.append(config.JSON_RAW_FEED_DIRECTORY_PATH + "/" + file)

    connectivity_check_daily_feed_filename = "connectivity-check-daily-feed-" + str(timestamp_minus_24hrs) + ".json"
    merge_files(raw_feed_connectivity_check_list,
                connectivity_check_daily_feed_filename, config.JSON_DAILY_FEED_DIRECTORY_PATH + "/pending")

    modem_status_daily_feed_filename = "modem_status-daily-feed-" + str(timestamp_minus_24hrs) + ".json"
    merge_files(raw_feed_modem_status_list,
                modem_status_daily_feed_filename, config.JSON_DAILY_FEED_DIRECTORY_PATH + "/pending")


def merge_files(file_list, destination_file, directory_name):
    try:
        os.makedirs(directory_name, exist_ok=True)
        #boto3.client('s3').get_object()
 # TODO correct merging into valid JSON dict, not list
        top_level_key = ""
        if len(destination_file) == 45:
            top_level_key = "connectivity_check_entries"
        else:
            top_level_key = "modem_status_entries"

        daily_feed = {}
        entry_list = []
        for file in file_list:

            with open(file) as f:
                try:
                    entry_list.append(json.load(f))
                except (JSONDecodeError, TypeError) as e:
                    logging.error(e)
        daily_feed[top_level_key] = entry_list
        with open(directory_name + "/" + destination_file, 'w', encoding='utf-8') as f:
            json.dump(daily_feed, f, ensure_ascii=False, indent=4)

    except OSError as e:
        logging.error(e)


def move_file(file, src_dir, dest_dir):
    try:
        os.makedirs(src_dir, exist_ok=True)
        os.makedirs(dest_dir, exist_ok=True)
        os.rename(src_dir + "/" + file, dest_dir + "/" + file)
    except OSError as e:
        logging.error(e)


config.setup_logging()
merge_raw_feed_json_files_to_daily_feed_json()
#upload_daily_feed_to_s3()
