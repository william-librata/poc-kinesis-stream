#!./venv/bin/python

from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub, SubscribeListener
import json


channel_name = 'pubnub-twitter'

pnconfig = PNConfiguration()
pnconfig.subscribe_key = 'sub-c-78806dd4-42a6-11e4-aed8-02ee2ddab7fe'
pnconfig.ssl = False

pubnub = PubNub(pnconfig)

my_listener = SubscribeListener()
pubnub.add_listener(my_listener)
pubnub.subscribe().channels(channel_name).execute()
my_listener.wait_for_connect()
print('connected')

counter = 1
while(counter <= 1):
    result = json.dumps(my_listener.wait_for_message_on(channel_name).message)
    print(result)
    counter += 1

pubnub.unsubscribe()
print('unsubscribed')
