# Arrow DB PythonScript

import pyarrow as pa # Apache Arrow
import pyarrow.json as pjson # Apache Arrow JSON
import paho.mqtt.client as mqtt
from datetime import datetime
import tempfile
import time
import json

def on_connect(client, userdata, flags, rc):
    if( rc == 0 ):
        print("Connected to broker.")
        global connected
        connected = True
    else:
        print("Cannot connect to broker.")

def on_message(client, userdata, message):
    global database
    
    # Decode the JSON payload
    payload_dict = json.loads(message.payload)
    
    # Generate timestamp
    timestamp = get_time()
    
    # Modify the payload to match the database schema
    for module_name, module_data in payload_dict.items():
        module_data["Timestamp"] = timestamp
    
    # Convert the modified payload back to a JSON string
    json_str = json.dumps(payload_dict)
    
    # Write the JSON string to a temporary file
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(json_str.encode())
        temp_file.seek(0)
        # Read the temporary file using PyArrow
        table = pjson.read_json(temp_file.name)
    
    # Concatenate the new table with the existing database
    database = pa.concat_tables([database, table])
    
    # Print the table
    print(database)

# Define a function to generate a timestamp
def get_time():
    return datetime.now().strftime("%m/%d/%Y %H:%M:%S")

# Database Schema
schema = pa.schema([
    ("Antenna", pa.struct([
        ("Time", pa.timestamp("s")),
        ("Status", pa.bool_()),
        ("Strength", pa.int64()),
        ("Connections", pa.int64())
    ])),
    ("ComputerSystem", pa.struct([
        ("Time", pa.timestamp("s")),
        ("Status", pa.bool_()),
        ("Direction", pa.string()),
        ("Speed", pa.float64())
    ])),
    ("Engine", pa.struct([
        ("Time", pa.timestamp("s")),
        ("Status", pa.bool_()),
        ("Temperature", pa.float64()),
        ("Pressure", pa.int64()),
        ("RPM", pa.int64())
    ])),
    ("Thruster", pa.struct([
        ("Time", pa.timestamp("s")),
        ("Status", pa.bool_()),
        ("Power", pa.int64()),
        ("Fuel", pa.int64())
    ])),
    ("Temperature", pa.struct([
        ("Time", pa.timestamp("s")),
        ("Status", pa.bool_()),
        ("Value", pa.float64()),
        ("Heater", pa.bool_())
    ]))
])

database = pa.Table.from_batches([], schema=schema)

# Connected status
connected = False

# MQTT Parameters
broker_name = "localhost"
broker_port = 1883
CID = "ArrowDB"
topic = "JsonTestTopic"

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
except KeyboardInterrupt:
    print("Exiting...")
    client.disconnect()
    client.loop_stop()




