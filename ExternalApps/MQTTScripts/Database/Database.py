"""
    Database v2.0
"""
import os
import time
import pyarrow as pa
from datetime import datetime
import paho.mqtt.client as mqtt

# Path
sessions_path = os.path.join(os.getcwd(), "Database", "Sessions")
file_path     = None

# Topics
simulation_topic = "SimulationTopic"
uuid_topic       = "UUIDTopic"
pid_topic        = "PIDTopic"

# Database
schema = pa.schema([
    ("Time", pa.timestamp('ms')),
    ("Data", pa.string())
])
database = pa.Table.from_batches([], schema=schema)

""" Callback Functions """

def connect_callback(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connected to broker.")
        # Subscribe to Topics
        client.subscribe(simulation_topic)
        client.subscribe(uuid_topic)
        # Publish PID
        print("Publishing PID.", end=" ")
        client.publish(pid_topic, payload="pid" + str(os.getpid()))
    else:
        print("Failed to connect to broker.")

def message_callback(client, userdata, msg):
    global file_path
    global database

    message = msg.payload.decode('utf-8')
    topic = msg.topic

    if topic == simulation_topic:
        global database
        temp = pa.Table.from_pydict({"Time": [int(time.time() * 1000)], "Data": [message]}, schema=schema)
        database = pa.concat_tables([database, temp])
        database.to_pandas().to_parquet(file_path)
        timestamp = datetime.now().strftime("%m/%d/%Y %I:%M:%S.%f")[:-3]
        print(f"[{timestamp}] Data added. (row: {database.num_rows})")
        return
    if topic == uuid_topic:
        timestamp = datetime.fromtimestamp(time.time()).strftime("%m-%d-%Y-%I-%M-%S-%p")
        #print(f"Received UUID: {message}")
        file_path = os.path.join(sessions_path, f"{timestamp}--{message}.parquet")
        database.to_pandas().to_parquet(file_path)
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

""" Main Function """

def main():

    # Client parameters
    cid  = "Database"
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
        print("Database is running.")
        client.loop_forever()
    except KeyboardInterrupt or Exception:
        client.disconnect()

if __name__ == "__main__":
    main()