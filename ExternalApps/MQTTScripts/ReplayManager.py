""" 
    Replay Manager v2.0 (based on original ReplayManagerV1.py)
    Responsible for managing the replay session data and sending it to UE using MQTT.
"""

import os
import json
import pandas as pd
import pyarrow.parquet as parq
import paho.mqtt.client as mqtt

""" Global Variables """

# Path
sessions_path = os.path.join(os.getcwd(), "Database\\PastSessionStorage")

#Topics
replay_topic      = "ReplayTopic"
replay_uuid_topic = "ReplayUUIDTopic"
replay_data_topic = "ReplayDataTopic"

# Data
session_data = None
module_data  = None
module_name  = None
member_name  = None

""" Callback Functions """

def connect_callback(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connected to broker.")
        # Subscribe to Topics
        client.subscribe(replay_topic)
        client.subscribe(replay_uuid_topic)
    else:
        print("Failed to connect to broker.")

def message_callback(client, userdata, msg):
    global module_name
    global member_name

    message = msg.payload.decode('utf-8')
    topic = msg.topic

    # Replay Topic Message
    if topic == replay_topic:
        match message:
            # Commands
            case "Start":
                # Start Sending Module Data to UE
                print("Replay session started.")
                return
            case "End":
                # End Sending Module Data to UE [End Game, End Replay, Terminal Off]
                print("Replay session ended. Connection from Unreal Engine client closed.")
                return
            case "List":
                # Send Session List to UE
                print("Publishing session list.", end=" ")
                publish_session_list(client)
                return
            # Module Selection
            case "Antenna":
                print(f"Module '{message}' selected.")
                module_name = message
                publish_module_members(client, member=message)
                return
            case "ComputerSystem":
                print(f"Module '{message}' selected.")
                module_name = message
                publish_module_members(client, member=message)
                return
            case "Engine":
                print(f"Module '{message}' selected.")
                module_name = message
                publish_module_members(client, member=message)
                return 
            case "Thruster":
                print(f"Module '{message}' selected.")
                module_name = message
                publish_module_members(client, member=message)
                return
            case "Temperature":
                print(f"Module '{message}' selected.")
                module_name = message
                publish_module_members(client, member=message)
                return
            case _:
                # Module Data Member
                if message.startswith("Type:"):
                    member_name = message.split(":")[1]
                    print(f"Member '{member_name}' of module '{module_name}' selected.")
                    publish_module_data(client)
                    return
                else:
                    # Miscellanous Messages
                    #print(f"msg = {message}")
                    return
    # Replay UUID Topic Message
    if topic == replay_uuid_topic:
        publish_session_found(client, message)
        return

def disconnect_callback(client, userdata, reason_code, properties):
    if reason_code == 0:
        print("Disconnected from broker.")
    else:
        print("Failed to disconnect from broker.")

def publish_callback(client, userdata, mid):
    print(f"Message published. (mid = {mid})")

def subscribe_callback(client, userdata, mid, reason_code_list, properties):
    if reason_code_list[0] == 0:
        print(f"Subscribed to topic. (mid = {mid})")
    else:
        print(f"Failed to subscribe topic. (mid = {mid})")

""" Functions """

def find_sessions():
    try:
        files = [file for file in os.listdir(sessions_path) if os.path.isfile(os.path.join(sessions_path, file))]
        return files
    except OSError as e:
        print(f"Error: {e}")
        return None

def open_session(client, file=None):
    global session_data
    if file is not None:
        print(f"Opening session '{file}'.")
        session_data = parq.read_table(os.path.join(sessions_path, file)).to_pandas()
        print("Publishing file found.", end=" ")
        client.publish(replay_uuid_topic, "FileFound")
    else:
        print("No file provided.")
        session_data = None
        print("Publishing file not found.", end=" ")
        client.publish(replay_uuid_topic, "FileNotFound")

def publish_session_list(client):
    sessions = find_sessions()
    if sessions is not None:
        client.publish(replay_topic, json.dumps({"SessionList": sessions}))
    return

def publish_session_found(client, msg):
    found = False
    if msg not in ["Empty", "FileFound", "FileNotFound"]:
        files = find_sessions()
        if files is not None:
            for file in files:
                if msg in file:
                    found = True
                    open_session(client, file)
                    return
            if not found:
                print("Failed to find session with that UUID.")
                return
        else:
            print("No sessions available in the directory.")
            client.publish(replay_uuid_topic, "FileNotFound")
            return

def publish_module_members(client, member=None):
    global module_data
    temp = []
    if member and session_data is not None:
        for idx, data in session_data['Data'].items():
            if member in json.loads(data):
                temp.append(json.loads(data)[member])
                if idx == 0 and temp is not None:
                    print("Publishing module's members.", end=" ")
                    client.publish(replay_topic, json.dumps({"ModuleDataType": temp[idx]}))
            else:
                print(f"Key '{member}' not found in session data.\n")
        module_data = pd.Series(temp, name=member)
    else:
        print("Key not found or session data is empty.\n")
        module_data = None

def publish_module_data(client):
    global module_data
    global member_name

    if module_data is None or member_name is None:
        print("Error: Module data or data type is 'None'!\n")
        return

    data = json.dumps({"Data": [item.get(member_name) for item in module_data]})

    print(f"Publishing module data:\n\t{data}", end="\n\t")
    client.publish(replay_data_topic, data, qos=1)
    return

""" Main Function """

def main():

    # Client parameters
    cid  = "ReplayManager"
    host = "localhost"
    port = 1883

    # Create a client instance
    client = mqtt.Client(client_id=cid, protocol=mqtt.MQTTv5, transport="tcp")
    client.max_queued_messages_set   = 0
    client.max_inflight_messages_set = 0

    # Assign callbacks
    client.on_connect = connect_callback
    client.on_disconnect = disconnect_callback
    client.on_message = message_callback
    client.on_publish = publish_callback
    client.on_subscribe = subscribe_callback

    # Connect to the broker
    client.connect(host=host, port=port, keepalive=60, clean_start=True)

    try:
        print("Replay Manager is running.")
        client.loop_forever()
    except KeyboardInterrupt or Exception:
        client.disconnect()

if __name__ == "__main__":
    main()