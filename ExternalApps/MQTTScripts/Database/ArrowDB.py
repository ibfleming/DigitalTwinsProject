# Arrow DB PythonScript

import pyarrow as pa # Apache Arrow
import pyarrow.csv
import pyarrow.parquet as parq # Parquet
import paho.mqtt.client as mqtt
import numpy as np
import time

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
topic = "SimulationTopic"

# Functions

def write_parquet_data(table, storageName):
    parq.write_table(table, storageName, compression=None)

def read_parquet_data(table):
    tempTable = parq.read_table(table)
    #print("\n-----------------------Look there is data-------------\n")
    print(tempTable)

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
    #print(db)

# Client
client = mqtt.Client(CID)
client.on_connect = on_connect
client.on_message = on_message
client.connect(broker_name, port=broker_port)
client.loop_start()

while connected is not True:
    time.sleep(0.1)

client.subscribe(topic)

try:
    while True:
        # Storage Table Name
        storage = "test_parquet_table.parquet"

        time.sleep(1)
<<<<<<< Updated upstream
=======
        write_parquet_data(db, storage)
        read_parquet_data(storage)
        write_parquet_data_to_disk()
        #print(db)
>>>>>>> Stashed changes
except KeyboardInterrupt:
    print("Exiting...")
    client.disconnect()
    client.loop_stop()




