import os
import paho.mqtt.publish
import pyarrow as pa
import pyarrow.parquet as parq
import paho.mqtt.client as mqtt
import time

# Storage file name
storage = "test_parquet_table.parquet"

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

# MQTT Session Param
simulation_topic = "SimulationTopic"
uuid_topic       = "UUIDTopic"
pid_topic        = "PIDTopic"

# Functions

def write_parquet_data(table, storageName):
    parq.write_table(table, storageName, compression=None)

def read_parquet_data(table):
    pass

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker!\n")
        global connected
        connected = True
    else:
        print("Cannot connect to broker.")

def on_message(client, userdata, message):
    global db
    # Get the current timestamp
    if message.topic == simulation_topic:
        current_time_ms = int(time.time() * 1000)
        # Append the new data to the database
        data = pa.Table.from_pydict({"Time": [current_time_ms], "Data": [message.payload.decode('utf-8')]}, schema=schema)
        # Concatenate the new table with the existing database
        db = pa.concat_tables([db, data])
        # print(db)
    elif message.topic == uuid_topic:
        print(message.payload)

# Functions
        
def publish_pid(pid):
   try:
      paho.mqtt.publish.single(pid_topic, payload="pid" + str(pid), qos=0, retain=False, hostname=broker_name,
                               port=broker_port, client_id=CID, keepalive=60, will=None, auth=None,
                                 tls=None, protocol=paho.mqtt.client.MQTTv5, transport="tcp")
   except Exception as e:
        print("Error:", e)        

# Main

def main():

    pid = os.getpid()
    publish_pid(pid)
    
    print("====================================")
    print(f"\tDatabase (PID: {pid})\t")
    print("====================================\n")

    # Client
    client = mqtt.Client(CID)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker_name, port=broker_port)
    client.loop_start()

    while not connected:
        time.sleep(0.1)

    client.subscribe(simulation_topic)
    client.subscribe(uuid_topic)
    client.subscribe(pid_topic)

    try:
        while True:
            time.sleep(1)
            read_parquet_data(storage)
    except KeyboardInterrupt:
        print("Exiting...")

        # Write the data when finished
        write_parquet_data(db, storage)

        client.disconnect()
        client.loop_stop()

if __name__ == "__main__":
    main()
