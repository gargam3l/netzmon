import json
import boto3
import uuid
import logging


def lambda_handler(event, context):
    # S3 python usage: https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/s3.html#examples

    for record in event["Records"]:
        bucket_name = record["s3"]["bucket"]["name"]
        filename = record["s3"]["object"]["key"]
        raw_json = read_file_from_s3(bucket_name, filename)
        feed_type = ""
        if len(filename) == 45:
            feed_type = "connectivity check"
        elif len(filename) == 39:
            feed_type = "modem status"

        item_dict = convert_json_record_to_item(raw_json, feed_type)

        if feed_type == "connectivity check":

            add_record_list_to_dynamodb_table("netzmon.connectivityCheck", item_dict["connectivity_check"])

        elif feed_type == "modem status":
            add_record_list_to_dynamodb_table("netzmon.modemStatus", item_dict["modem_status"])
            add_record_list_to_dynamodb_table("netzmon.correctableSummary", item_dict["correctable_summary"])
            add_record_list_to_dynamodb_table("netzmon.dsChannelList", item_dict["ds_channel_list"])
            add_record_list_to_dynamodb_table("netzmon.usChannelList", item_dict["us_channel_list"])

    print("bucket name: " + bucket_name + " - file name: " + filename)
    print("feed type " + feed_type)
    print("json: " + str(raw_json))
    print("key: " + "function_name" + " - value: " + context.function_name)
    print("key: " + "invoked_function_arn" + " - value: " + context.invoked_function_arn)
    return {
        'statusCode': 200,
        'body': json.dumps('Hello from Lambda!')
    }


def read_file_from_s3(bucket_name, filename):
    s3_client = boto3.client('s3')
    response = ''
    try:
        response = s3_client.get_object(Bucket=bucket_name, Key=filename)
    except Exception as e:
        logging.error(e)

    return response['Body'].read()


def add_record_list_to_dynamodb_table(table_name, record_list):
    client = boto3.client('dynamodb')
    for record in record_list:
        try:
            response = client.put_item(TableName=table_name, Item=record)
            logging.info("Dynamo DB record creation response: " + str(response))
        except Exception as e:
            logging.error(e)


def convert_json_record_to_item(raw_json, feed_type):
    item_list = []
    input = json.loads(raw_json)
    if feed_type == "connectivity check":
        for record in input:
            item = {
                "connectivity_check_id": {
                    "S": str(uuid.uuid4())
                },
                "destination": {
                    "S": str(record['ping result']['destination'])
                },
                "host_type": {
                    "S": str(record['host'])
                },
                "packet_loss_rate": {
                    "N": str(record['ping result']['packet_loss_rate'])
                },
                "rtt_avg": {
                    "N": str(record['ping result']['rtt_avg'])
                },
                "rtt_max": {
                    "N": str(record['ping result']['rtt_max'])
                },
                "rtt_min": {
                    "N": str(record['ping result']['rtt_min'])
                },
                "timestamp": {
                    "N": str(record['timestamp'])
                }
            }
            item_list.append(item)
        return {"connectivity_check": item_list}
    elif feed_type == "modem status":
        item_dict = {}
        item = {}
        for block in input["modem_status_entries"]:
            timestamp = block['timestamp']
            print("block type " + str(type(block)))
            for key in block:
                item_list = []
                print("key type " + str(type(key)))
                print("block[key] type " + str(type(block[key])))
                for record in block[key]:
                    if key == "modem_status":

                        item = {
                            "comment": {
                                "S": str(record['Comment'])
                            },
                            "modem_status_id": {
                                "S": str(uuid.uuid4())
                            },
                            "procedure": {
                                "S": str(record['Procedure'])
                            },
                            "status": {
                                "S": str(record['Status'])
                            },
                            "timestamp": {
                                "N": str(timestamp)
                            }
                        }

                    elif key == "ds_channel_list":
                        item = {
                            "channel_status_id": {
                                "S": str(uuid.uuid4())
                            },
                            "timestamp": {
                                "N": str(timestamp)
                            },
                            "channel": {
                                "S": str(record['Channel'])
                            },
                            "frequency": {
                                "S": str(record['Frequency'])
                            },
                            "power": {
                                "S": str(record['Power'])
                            },
                            "snr": {
                                "S": str(record['SNR'])
                            },
                            "correctables": {
                                "S": str(record['Correctables'])
                            },
                            "uncorrectables": {
                                "S": str(record['Uncorrectables'])
                            }
                        }
                    elif key == "correctable_summary":
                        item = {
                            "correctable_id": {
                                "S": str(uuid.uuid4())
                            },
                            "timestamp": {
                                "N": str(timestamp)
                            },
                            "total_correctables": {
                                "N": str(record['Total Correctables'])
                            },
                            "total_uncorrectables": {
                                "N": str(record['Total Uncorrectables'])
                            }
                        }

                    elif key == "us_channel_list":
                        item = {
                            "us_channel_status_id": {
                                "S": str(uuid.uuid4())
                            },
                            "timestamp": {
                                "N": str(timestamp)
                            },
                            "channel": {
                                "S": str(record['Channel'])
                            },
                            "symbol_rate": {
                                "S": str(record['Symbol Rate'])
                            },
                            "frequency": {
                                "S": str(record['Frequency'])
                            },
                            "power": {
                                "S": str(record['Power'])
                            }
                        }
                    item_list.append(item)
                item_dict[key] = item_list

        return item_dict


