"""
    Replay Manager Script
"""

import os
import paho.mqtt.client as mqtt

import pandas as pd
import time
import json
import pyarrow.parquet as parq

# Status
connected = False
replay    = False

# MQTT Parameters
broker_name = "localhost"
broker_port = 1883
CID         = "ReplayManager"

#Topics
replay_topic      = "ReplayTopic"
replay_uuid_topic = "ReplayUUIDTopic"
replay_data_topic = "ReplayDataTopic"

# Database Absolute Path
sessions_path    = os.path.join(os.getcwd(), "Database\\PastSessionStorage")
session_data     = None
module_data      = None
module_name      = None
module_data_type = None

"""
    Callback Functions
"""

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("CONNECTED TO BROKER.\n")
        global connected
        connected = True
    else:
        print("CONNECTING TO BROKER FAILED.\n")

def on_message(client, userdata, message):

    global session_data
    global module_data
    global module_name
    global module_data_type

    global replay_topic
    global replay_uuid_topic
    global replay_data_topic

    msg = message.payload.decode('utf-8')
    topic = message.topic

    # Replay Topic
    if topic == replay_topic:
        match msg:

            # Commands
            case "Start":
                # Start Sending Module Data to UE
                print("Start Received...\n")
                return

            case "End":
                # End Sending Module Data to UE [End Game, End Replay, Terminal Off]
                print("End Received...\n")
                reset()
                return

            case "List":
                # Send Session List to UE
                publish_session_list(client)
                print("Sending Session List...\n")
                return
            
            # Module Selection
            case "Antenna":
                print("User selected 'Antenna' module.\n")
                module_name = msg
                populate_module_data(client, msg)
                return
            
            case "ComputerSystem":
                print("User selected 'Computer System' module.\n")
                module_name = msg
                populate_module_data(client, msg)
                return
            
            case "Engine":
                print("User selected 'Engine' module.\n")
                module_name = msg
                populate_module_data(client, msg)
                return
            
            case "Thruster":
                print("User selected 'Thruster' module.\n")
                module_name = msg
                populate_module_data(client, msg)
                return
            
            case "Temperature":
                print("User selected 'Temperature' module.\n")
                module_name = msg
                populate_module_data(client, msg)
                return
            
            # Default
            case _:
                # Selected Module Data Type Message
                if msg.startswith("T:"):
                    module_data_type = msg.split(":")[1]
                    print(f"User selected '{module_data_type}' data type.\n")
                    publish_module_data(client)
                else:
                    # Backflow of miscellaneous messages in brokers
                    print(f"msg = {msg}\n")
                return
            
    # Replay UUID Topic
    if topic == replay_uuid_topic:
        if msg is not ["Empty", "FileFound", "FileNotFound"]:
            files = read_sessions()
            if files:
                for file in files:
                    if msg in file:
                        print(f"Selected File: {file}\n")
                        open_file(file)
                        client.publish(replay_uuid_topic, "FileFound")
                        break
            else:
                print("No sessions available.\n")
        return
    
    # Replay Data Topic
    if topic == replay_data_topic:
        # Nothing...
        return

    print(f"Unknown topic. msg = {msg}")
    return

"""
    Utility Functions
"""
# Read Sessions
def read_sessions():
    try:
        files = [file for file in os.listdir(sessions_path) if os.path.isfile(os.path.join(sessions_path, file))]
        return files
    except OSError as e:
        print(f"Error: {e}")
        return None

# Publish Session List
def publish_session_list(client):
    sessions = read_sessions()
    if sessions is not None:
        json_object = {"SessionList": sessions}
        client.publish(replay_topic, json.dumps(json_object))
    return

# Publish: Iterate Module Database
# client = use this as the publishing client
# global module_data = use this as the data source
# global module_data_type = use this as the data type to select the specified data from the module data
def publish_module_data(client):
   
    global module_data
    global module_data_type

    if module_data is None and module_data_type is None:
        print("Error: Module data or data type is 'None'!\n")
        return
    
    for data in module_data:
        for key, value in data.items():
            if key == module_data_type:
                print(f"{key}: {value}")
                client.publish(replay_data_topic, json.dumps({key: value}))
                time.sleep(1)
    return


# Open File for Reading
def open_file(file):
    global session_data
    file_path = os.path.join(sessions_path, file)
    session_data = parq.read_table(file_path).to_pandas()

# Populate Module Data
def populate_module_data(client, key=None):
    global session_data
    global module_data
    temp = []
    if key and session_data is not None:
        for idx, data in session_data['Data'].items():
            if key in json.loads(data):
                temp.append(json.loads(data)[key])
                if idx == 0 and temp is not None:
                    client.publish(replay_topic, json.dumps({"ModuleDataType": temp[idx]}))
            else:
                print(f"Key '{key}' not found in session data.\n")
        module_data = pd.Series(temp, name=key)
        return True
    else:
        print("Key not found or session data is empty.\n")
        module_data = None
        return False

# Reset
def reset():
    global session_data
    global module_data
    global module_name
    global module_data_type

    session_data     = None
    module_data      = None
    module_name      = None
    module_data_type = None

"""
    Main Function
"""

def main():

    print("\n==============================")
    print("\tReplay Manager\t")
    print("==============================")

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
    client.subscribe(replay_data_topic)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...\n")
        client.disconnect()
        client.loop_stop()

if __name__ == "__main__":
    main()