#!../venv/bin/python

import boto3
import time
import datetime
import json
import ast
from decimal import Decimal


def remove_empty_string(dic):
    for e in dic:
        if isinstance(dic[e], dict):
            dic[e] = remove_empty_string(dic[e])
        if (isinstance(dic[e], str) and dic[e] == ""):
            dic[e] = None
        if isinstance(dic[e], type(list)):
            for entry in dic[e]:
                remove_empty_string(entry)
    return dic


def consumer_exists(stream_arn, consumer_name):
    try:
        response = client.describe_stream_consumer(
            StreamARN=stream_arn,
            ConsumerName=consumer_name
        )
        return True
    except client.exceptions.ResourceNotFoundException:
        return False


def register_consumer(stream_arn, consumer_name, force=False):

    # check if exists
    if consumer_exists(stream_arn, consumer_name):
        print('Consumer exists')
        if force:
            deregister_consumer(stream_arn, consumer_name)
        else:
            return

    # register consumer
    response = client.register_stream_consumer(
        StreamARN=stream_arn,
        ConsumerName=consumer_name
    )
    consumer_arn = response['Consumer']['ConsumerARN']
    consumer_status = response['Consumer']['ConsumerStatus']

    # wait until consumer active
    while consumer_status != 'ACTIVE':
        time.sleep(5)
        response = client.describe_stream_consumer(
            StreamARN=stream_arn,
            ConsumerName=consumer_name
        )
        consumer_status = response['ConsumerDescription']['ConsumerStatus']

    return consumer_arn


def deregister_consumer(stream_arn, consumer_name):
    response = client.deregister_stream_consumer(
        StreamARN=stream_arn,
        ConsumerName=consumer_name
    )

    while consumer_exists(stream_arn, consumer_name):
        time.sleep(5)


def fetch_records(stream_name, stream_arn, shard_id, consumer_name, consumer_arn):

    # get dynamodb table to be inserted
    table = get_dynamodb_table('SensorNetworkData')

    response = client.subscribe_to_shard(
        ConsumerARN=consumer_arn,
        ShardId=shard_id,
        StartingPosition={'Type': 'TRIM_HORIZON'}
    )

    shard_iterator = client.get_shard_iterator(StreamName=stream_name,
                                               ShardId=shard_id,
                                               ShardIteratorType='TRIM_HORIZON')['ShardIterator']

    counter = 0
    while(True and counter < 10000):

        response = client.get_records(ShardIterator=shard_iterator)
        shard_iterator = response['NextShardIterator']
        if len(response['Records']) > 0:
            data = json.loads(response['Records'][0]['Data'], parse_float=Decimal)
            print('Processing sensor: %s', data['sensor_uuid'])
            data_fix = remove_empty_string(data)
            try:
                '''
                table.put_item(
                    Item=data_fix
                )
                '''
                print(data_fix)
                counter += 1

            except:
                print('ERROR : ')
        else:
            print('Waiting..')
            time.sleep(5)


if __name__ == '__main__':

    stream_name = 'DataStream'
    consumer_name = 'StreamConsumer3'

    # setup dynamodb
    dynamodb = boto3.resource('dynamodb')
    table = dynamodb.Table('DataStream')

    # setup kinesis
    client = boto3.client('kinesis')

    # get stream details
    response = client.describe_stream(StreamName=stream_name)
    stream_arn = response['StreamDescription']['StreamARN']
    shard_id = response['StreamDescription']['Shards'][2]['ShardId']

    # get consumer details
    response = client.describe_stream_consumer(
        StreamARN=stream_arn,
        ConsumerName=consumer_name
    )
    consumer_arn = response['ConsumerDescription']['ConsumerARN']

    # subscribe to shard
    response = client.subscribe_to_shard(
        ConsumerARN=consumer_arn,
        ShardId=shard_id,
        StartingPosition={'Type': 'TRIM_HORIZON'}
    )

    # iterate event stream
    for event in response['EventStream']:
        print(event)
        if len(event['SubscribeToShardEvent']['Records']) > 0:
            # if records are not empty
            for record in event['SubscribeToShardEvent']['Records']:
                data = remove_empty_string(json.loads(record['Data'], parse_float=Decimal))
                print(data)
                table.put_item(Item=data)

