#!./venv/bin/python

from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub, SubscribeListener


channel_name = 'pubnub-sensor-network'

pnconfig = PNConfiguration()
pnconfig.subscribe_key = 'sub-c-5f1b7c8e-fbee-11e3-aa40-02ee2ddab7fe'
pnconfig.ssl = False

pubnub = PubNub(pnconfig)

my_listener = SubscribeListener()
pubnub.add_listener(my_listener)
pubnub.subscribe().channels(channel_name).execute()
my_listener.wait_for_connect()
print('connected')

counter = 1
while(counter < 100):
    print(my_listener.wait_for_message_on(channel_name).message)
    counter += 1

pubnub.unsubscribe()
print('unsubscribed')
