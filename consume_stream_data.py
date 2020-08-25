#!./venv/bin/python

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

#dict = json.loads('{"key1":"val1", "key2":"val2", "key3":"", "user": {"id": 1666401798, "id_str": "1666401798", "name": "", "test": 1}}')
#dict_fix = remove_empty_string(dict)
#print(dict_fix)






client = boto3.client('kinesis')

response = client.describe_stream(StreamName='TwitterDataStream')
#print(response)
#print(response['StreamDescription']['Shards'][0])
#print(response['StreamDescription']['Shards'][1])
#print(response['StreamDescription']['Shards'][2])

shard_id = response['StreamDescription']['Shards'][1]['ShardId']

print(shard_id)

the_time = datetime.datetime.now()

shard_iterator = client.get_shard_iterator(StreamName='TwitterDataStream', ShardId=shard_id,
                                           ShardIteratorType='TRIM_HORIZON')['ShardIterator']

# setup dynamodb conn
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('TwitterData')

counter = 0
while(True and counter < 10000):

    response = client.get_records(ShardIterator=shard_iterator, Limit=1)
    shard_iterator = response['NextShardIterator']
    if len(response['Records']) > 0:
        data = json.loads(response['Records'][0]['Data'], parse_float=Decimal)
        print('Processing id: $s', data['id'])
        data_fix = remove_empty_string(data)
        try:

            table.put_item(
                Item=data_fix
            )
            counter += 1

        except:
            print('ERROR : ')
            print('Raw data : %s', data)
            print('Fixed data : %s', data)
    else:
        print('Waiting..')
        time.sleep(5)

