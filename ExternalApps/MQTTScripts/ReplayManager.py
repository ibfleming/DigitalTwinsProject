"""
    Replay Manager Script
"""

import os
import paho.mqtt.client as mqtt
import pyarrow.parquet as parq
import pandas as pd
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
replay_uuid_topic = "ReplayUUIDTopic"

# Database Absolute Path
db_path = os.path.join(os.getcwd(), "Database\\PastSessionStorage")
replay_db = None

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
            match message.payload.decode('utf-8'):
                case "Start":
                    replay = True
                    print("Starting Replay Session...\n")
                    return
                case "List":
                    publish_session_list(client)
                    return
                case "Antenna":
                    print("User selected 'Antenna' module for replay.\n")
                    data = access_data_element(replay_db, message.payload.decode('utf-8'))
                    publish_module_data_list(client, data)
                    return
                case "ComputerSystem":
                    print("User selected 'Computer System' module for replay.\n")
                    print(access_data_element(replay_db, message.payload.decode('utf-8')))
                    return
                case "Engine":
                    print("User selected 'Engine' module for replay.\n")
                    print(access_data_element(replay_db, message.payload.decode('utf-8')))
                    return
                case "Thruster":
                    print("User selected 'Thruster' module for replay.\n")
                    print(access_data_element(replay_db, message.payload.decode('utf-8')))
                    return
                case "Temperature":
                    print("User selected 'Temperature' module for replay.\n")
                    print(access_data_element(replay_db, message.payload.decode('utf-8')))
                    return
                case _:
                    return
        if message.topic == replay_uuid_topic:
            if message.payload.decode('utf-8') != "Empty" and message.payload.decode('utf-8') != "FileFound":
                uuid = message.payload.decode('utf-8')
                files = read_sessions()
                if files:
                    for file in files:
                        if uuid in file:
                            print("Selected File for Replay: " + file, end="\n\n")
                            open_file(file)
                            client.publish(replay_uuid_topic, "FileFound")
                            break
                else:
                    print("No sessions available.\n")    
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

def publish_module_data_list(client, data):
    json_object = {"ModuleDataType": data[0]}
    client.publish(replay_topic, json.dumps(json_object))
    print("Sending data type for client to select...\n")

def publish_db_value(client, data):
    client.publish(replay_topic, str(data))

def open_file(file):
    global replay_db
    file_path = db_path + "\\" + file
    replay_db = parq.read_table(file_path).to_pandas()

def access_data_element(db=replay_db, key=None):
    result_data = []
    if key is not None:
        for idx, data in db['Data'].items():
            json_data = json.loads(data)
            if key in json_data:
                result_data.append(json_data[key])
            else:
                print(f"Key '{key}' not found in row {idx}\n")
        result_data = pd.Series(result_data, name=key)
        return result_data        
    else:
        return None

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
    client.subscribe(replay_uuid_topic)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
        client.disconnect()
        client.loop_stop()

if __name__ == "__main__":
    main()