#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MQTT Script for Digital Twins Project
2/12/2024

Script that changes the temerature of the ship randomly
every 2 seconds. 

This value will be randomly generated between the values 0 and 100 (Degrees Farenhieght)
"""

import paho.mqtt.publish
import paho.mqtt.client
import time
import random

# Constants:
CONST_broker_name = "localhost"
CONST_broker_port = 1883
CONST_clientID = "CID"
CONST_topicStr = "ShipTemperatureTopic"

CONST_max_messages = 1000
CONST_time_delay = 2

def post_temperature_change():
    global status  # Declare status as global
    for i in range(CONST_max_messages):
        time.sleep(CONST_time_delay)
        temerature_msg = random.uniform(0.0, 100.0)
        # Publish to Subscribers
        print(f"-- Publishing: {temerature_msg}, to Topic: {CONST_topicStr}, to Broker: {CONST_broker_name}.")
        paho.mqtt.publish.single(CONST_topicStr, payload=temerature_msg, qos=0, retain=False, hostname=CONST_broker_name,
                                 port=CONST_broker_port, client_id=CONST_clientID, keepalive=60, will=None, auth=None,
                                 tls=None, protocol=paho.mqtt.client.MQTTv5, transport="tcp")

# Callbacks

def on_publish(client, userdata, mid):
    print(f"-- Callback: Published message with mid: {str(mid)}.")

# Main:

def main():
    random.seed(7)
    post_temperature_change()

if __name__ == '__main__':
    main();