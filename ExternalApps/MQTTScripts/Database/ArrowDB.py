# Arrow DB PythonScript

import pandas as pd
import pyarrow as pa # Apache Arrow
import pyarrow.json as pjson # Apache Arrow JSON
import paho.mqtt.client as mqtt
from datetime import datetime
import time
import json

# Define the schema
schema = pa.schema([
    ("Time", pa.timestamp('ms')),
    ("Data", pa.string())
])

# PyArrow Database
db = pa.Table.from_batches([], schema=schema)

# Connected status
connected = False

# MQTT Parameters
broker_name = "localhost"
broker_port = 1883
CID = "ArrowDB"
topic = "JsonTestTopic"

# Functions

def on_connect(client, userdata, flags, rc):
    if( rc == 0 ):
        print("Connected to broker.")
        global connected
        connected = True
    else:
        print("Cannot connect to broker.")

def on_message(client, userdata, message):
    global db
    # Get the current timestamp
    current_time_ms = int(time.time() * 1000)
    # Append the new data to the database
    data = pa.Table.from_pydict({"Time": [current_time_ms], "Data": [message.payload.decode('utf-8')]}, schema=schema)
    # Concatenate the new table with the existing database
    db = pa.concat_tables([db, data])

# Client
client = mqtt.Client(CID)
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_name, port=broker_port)
client.loop_start()

while connected != True:
    time.sleep(0.1)

client.subscribe(topic)

try:
    while True:
        time.sleep(1)
        print(db)
except KeyboardInterrupt:
    print("Exiting...")
    client.disconnect()
    client.loop_stop()




