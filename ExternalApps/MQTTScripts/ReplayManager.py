"""
    Replay Manager Script
"""

import paho.mqtt.client as mqtt
import time

# Status
connected = False
replay    = False

# MQTT Parameters
broker_name = "localhost"
broker_port = 1883
CID = "ReplayManager"

#Topics
replay_topic = "ReplayTopic"

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
    elif replay:
        if message.topic == replay_topic:
            if message.payload.decode('utf-8') == "End":
                replay = False
                print("Ending Replay Session...\n")

"""
    Utility Functions
"""

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