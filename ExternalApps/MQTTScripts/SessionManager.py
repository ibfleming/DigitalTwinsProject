import platform
import subprocess
import paho.mqtt.publish as mqtt_publish
import paho.mqtt.client as mqtt
from datetime import datetime
import time
import uuid

connected = False
inSession = False

# Global UUID
baseUUID = uuid.uuid4()

# MQTT Parameters
broker_name = "localhost"
broker_port = 1883
CID = "SessionManager"
topic = "SessionTopic"

# UUID Topic
UUIDTopic = "UUIDTopic"

# Script Paths
database_script = "Database/ArrowDB.py"
simulation_script = "Simulation/Simulation.py"

# Callback Functions
def on_connect(client, userdata, flags, rc):
    if( rc == 0 ):
        print("Connected to broker successfully.\nAwaiting session start...")
        global connected
        connected = True
    else:
        print("Cannot connect to broker.")

def on_message(client, userdata, message):
    global inSession
    global baseUUID
    if not inSession:
        if message.payload.decode('utf-8') == "Start":
            inSession = True
            print("Creating session...")
            dispatch_script(database_script)
            dispatch_script(simulation_script)

            time.sleep(1)

            mqtt_publish.single(
                topic,
                f"[{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}] Session Created Successfully (UUID: {baseUUID})",
                qos=0,
                retain=False,
                hostname=broker_name,
                port=broker_port
            )

            mqtt_publish.single(
                UUIDTopic,
                str(baseUUID),
                qos=0,
                retain=False,
                hostname=broker_name,
                port=broker_port
            )
    elif message.payload.decode('utf-8') == "End":
        inSession = False
        print("Ending session...")

def on_publish(client, userdata, mid):
    print("Message {} sent from {}".format(mid, CID))

# Dispatch Scripts
def dispatch_script(script_path):
    try:
        if platform.system() == "Windows":
            subprocess.Popen(['start', 'cmd', '/c', 'python', script_path], shell=True)
        else:
            subprocess.Popen(['python', script_path], check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error executing script: {e}")

# Client
client = mqtt.Client(CID)
client.on_connect = on_connect
client.on_message = on_message
client.on_publish = on_publish
client.connect(broker_name, port=broker_port)
client.loop_start()

while not connected:
    time.sleep(0.1)

client.subscribe(topic)
client.subscribe(UUIDTopic)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Exiting...")
    client.disconnect()
    client.loop_stop()
