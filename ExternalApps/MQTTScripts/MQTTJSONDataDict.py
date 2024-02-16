#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MQTT Script for Digital Twins Project
2/16/2024

This will get the data for the ship in JSON format and then have MQTT send the JSON dict with all of the information. 
This way we can parse through all of the data on the side of UNREAL ENGINE instead of havign a billion scripts that get each 
piece of data for us.

"""

import paho.mqtt.publish
import paho.mqtt.client as mqtt
import json
import time

# Constants:
CONST_broker_name = "localhost"
CONST_broker_port = 1883
CONST_clientID = "CID"
CONST_topicStr = "JSONDATA"

CONST_max_messages = 1000
CONST_time_delay = 5

payload = None

#this is just to test
dictionary = {
    "moduleName": "TestModule",
    "value": 10001,
    "status": "Online"
}

#Serialize the data
json_object = json.dumps(dictionary, indent=4)

def dictionary_data_to_be_compiled():

    #Write the data
    dictionary = {
        "moduleName": "TestModule",
        "value": 10001,
        "status": "Online"
    }

    #Serialize the data
    #global json_object = json.dumps(dictionary, indent=4)

    #writing to test file sample.json
    with open("sample.json", "w") as outfile:
        outfile.write(json_object)

def on_publish(client, userdata, mid):
    print("Message Published...")

def on_connect(client, userdata, flags, rc):
    client.subscribe(CONST_topicStr)
    client.publish(CONST_topicStr, json_object)

def on_message(client, userdata, msg):
    print(msg.topic)
    print(msg.payload) #<- do you mean this payload??
    payload = json.loads(msg.payload) #json.loads to convert the string to JSON
    print(payload['moduleName']) #Then you can check the value of anything in the message payload
    client.disconnect() #disconnect after recieving the payload

def post_status_change():
    global status  # Declare status as global
    for i in range(CONST_max_messages):
        time.sleep(CONST_time_delay)
    
        # Publish to Subscribers
        print(f"-- Publishing: , to Topic: {CONST_topicStr}, to Broker: {CONST_broker_name}.")
        paho.mqtt.publish.single(CONST_topicStr, payload=json_object, qos=0, retain=False, hostname=CONST_broker_name,
                                 port=CONST_broker_port, client_id=CONST_clientID, keepalive=60, will=None, auth=None,
                                 tls=None, protocol=paho.mqtt.client.MQTTv5, transport="tcp")

#start the client
mqttc = mqtt.Client()

#callbakc functions
mqttc.on_publish = on_publish
mqttc.on_connect = on_connect
mqttc.on_message = on_message

#conect with the MQTT broker
mqttc.connect(CONST_broker_name, CONST_broker_port, CONST_max_messages)

#just keep looping
mqttc.loop_forever()

# Main:
def main():
    post_status_change()
    #dictionary_data_to_be_compiled()

if __name__ == '__main__':
    main();