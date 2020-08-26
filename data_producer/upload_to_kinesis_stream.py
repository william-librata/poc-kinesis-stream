#!../venv/bin/python

from pubnub.pnconfiguration import PNConfiguration
from pubnub.pubnub import PubNub, SubscribeListener


channel_name = 'pubnub-sensor-network'
subscriber_key = 'sub-c-5f1b7c8e-fbee-11e3-aa40-02ee2ddab7fe'


def setup_pubnub():
    # setup config
    pnconfig = PNConfiguration()
    pnconfig.subscribe_key = subscriber_key
    pnconfig.ssl = False
    return PubNub(pnconfig)


def setup_listener(pubnub):
    listener = SubscribeListener()
    pubnub.add_listener(listener)
    pubnub.subscribe().channels(channel_name).execute()
    listener.wait_for_connect()
    return listener


def unsubscribe(pubnub, listener):
    # unsubscribe
    pubnub.unsubscribe().channels(channel_name).execute()
    listener.wait_for_disconnect()
    print('unsubscribed')


def upload_data():
    # setup data source
    pubnub = setup_pubnub()
    listener = setup_listener(pubnub)

    # setup counter
    counter = 1
    stop_counter = 10

    # loop
    while(counter < stop_counter):
        # send to kinesis stream
        data = listener.wait_for_message_on(channel_name).message
        print(data)
        counter += 1

    unsubscribe(pubnub, listener)


if __name__ == '__main__':
    upload_data()
