#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MQTT Script for Digital Twins Project
2/8/2024

Script that changes the status of the spaceship modules from
Online or Offline every 5 seconds.

"""

import paho.mqtt.publish
import paho.mqtt.client
import time

# Constants:
CONST_broker_name = "localhost"
CONST_broker_port = 1883
CONST_clientID = "CID"
CONST_topicStr = "ModuleStatusTopic"

CONST_max_messages = 1000
CONST_time_delay = 5

status = False

def post_status_change():
    global status  # Declare status as global
    for i in range(CONST_max_messages):
        time.sleep(CONST_time_delay)
        if status == False:
            # Send Online
            status = True
            messageStr = "Online"
        else:
            # Send Offline
            status = False
            messageStr = "Offline"
        # Publish to Subscribers
        print(f"-- Publishing: {messageStr}, to Topic: {CONST_topicStr}, to Broker: {CONST_broker_name}.")
        paho.mqtt.publish.single(CONST_topicStr, payload=messageStr, qos=0, retain=False, hostname=CONST_broker_name,
                                 port=CONST_broker_port, client_id=CONST_clientID, keepalive=60, will=None, auth=None,
                                 tls=None, protocol=paho.mqtt.client.MQTTv5, transport="tcp")

# Callbacks

def on_publish(client, userdata, mid):
    print(f"-- Callback: Published message with mid: {str(mid)}.")

# Main:

def main():
    post_status_change()

if __name__ == '__main__':
    main()