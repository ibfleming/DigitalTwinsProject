"""
    Replay Manager Script
"""

import os
import paho.mqtt.client as mqtt
import time
import json

# Status
connected = False
replay    = False

# MQTT Parameters
broker_name = "localhost"
broker_port = 1883
CID = "ReplayManager"

#Topics
replay_topic = "ReplayTopic"

# Database Absolute Path
db_path = os.path.join(os.getcwd(), "Database/PastSessionStorage")

"""
    Callback Functions
"""

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker!\n")
        global connected
        connected = True
    else:
        print("Cannot connect to broker.\n")

def on_message(client, userdata, message):
    global replay
    if not replay:
        if message.topic == replay_topic:
            if message.payload.decode('utf-8') == "Start":
                replay = True
                print("Starting Replay Session...\n")
            if message.payload.decode('utf-8') == "List":
                publish_session_list(client)
            else:
                pass
    elif replay:
        if message.topic == replay_topic:
            if message.payload.decode('utf-8') == "End":
                replay = False
                print("Ending Replay Session...\n")
            else:
                print(message.payload.decode('utf-8') + "\n")

"""
    Utility Functions
"""

def read_sessions():
    try:
        files = [file for file in os.listdir(db_path) if os.path.isfile(os.path.join(db_path, file))]
        return files
    except OSError as e:
        print(f"Error: {e}")
        return None

def publish_session_list(client):
    sessions = read_sessions()
    if sessions is not None:
        json_object = {"SessionList": sessions} # Convert to proper JSON format
        client.publish(replay_topic, json.dumps(json_object))

def publish_db_value(client, data):
    client.publish(replay_topic, str(data))

"""
    Main Function
"""

def main():

    print("\n==============================")
    print("\tReplay Manager\t")
    print("==============================\n")

    # Client
    client = mqtt.Client(CID)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker_name, port=broker_port)
    client.loop_start()

    while not connected:
        time.sleep(0.1)

    client.subscribe(replay_topic)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
        client.disconnect()
        client.loop_stop()

if __name__ == "__main__":
    main()