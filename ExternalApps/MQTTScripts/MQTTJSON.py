import paho.mqtt.publish
import paho.mqtt.client as mqtt
import json
import random
import time

# MQTT
broker_name = "localhost"
broker_port = 1883
CID = "CID"
topic = "JsonTestTopic"

# Constants
max_messages = 1000
time_delay = 5
status = False

# Function to generate a random integer within a given range
def generate_random_int(min_value, max_value):
    return random.randint(min_value, max_value)

# Function to generate a random float within a given range
def generate_random_float(min_value, max_value):
    return round(random.uniform(min_value, max_value), 1)

# Function to choose a random direction
def generate_random_direction():
    directions = ["N", "NW", "S", "SW", "E", "W", "SE", "NE"]
    return random.choice(directions)

def generate_random_status():
   statuses = [True, False]
   return random.choice(statuses)

# Dictionary/JSON to be published to Broker (MQTT)
json_data = {
   "Antenna": {
         "Status": generate_random_status(),
         "Strength": generate_random_int(0, 100),
         "Connections": generate_random_int(1, 10)
   },
   "ComputerSystem": {
         "Status": generate_random_status(),
         "Direction": generate_random_direction(),
         "Speed": generate_random_float(25, 100)
   },
   "Engine": {
         "Status": generate_random_status(),
         "Temperature": generate_random_float(-10, 72),
         "Pressure": generate_random_int(0, 100),
         "RPM": generate_random_int(500, 7200)
   },
   "Thruster": {
         "Status": generate_random_status(),
         "Power": generate_random_int(100, 1000),
         "Fuel": generate_random_int(0, 100)
   },
   "Temperature": {
         "Status": generate_random_status(),
         "Value": generate_random_float(0, 100)
   }
}

# Function to change the statuses of all modules
def change_module_status():
    global status
    status = not status  # Toggle the status between True and False
    for module, module_data in json_data.items():
        module_data["Status"] = status

def update_json(module, key, value):
   try:
      json_data[module][key] = value
   except:
      print("Invalid module or key provided.")

def generate_new_values():
   # Antenna   
   update_json("Antenna", "Status", generate_random_status())
   update_json("Antenna", "Strength", generate_random_int(0, 100))
   update_json("Antenna", "Connections", generate_random_int(1, 10))
   # Computer System
   update_json("ComputerSystem", "Direction", generate_random_direction())
   update_json("ComputerSystem", "Speed", generate_random_float(25, 100))
   # Engine
   update_json("Engine", "Temperature", generate_random_float(-10, 72))
   update_json("Engine", "Pressure", generate_random_int(0, 100))
   update_json("Engine", "RPM", generate_random_int(500, 7200))
   # Thruster
   update_json("Thruster", "Power", generate_random_int(0, 500))
   update_json("Thruster", "Fuel", generate_random_int(0, 100))
   #Temperature
   update_json("Temperature", "Value", generate_random_float(0, 100))

def publish():
   try:
      paho.mqtt.publish.single(topic, payload=json.dumps(json_data), qos=0, retain=False, hostname=broker_name,
                               port=broker_port, client_id=CID, keepalive=60, will=None, auth=None,
                                 tls=None, protocol=paho.mqtt.client.MQTTv5, transport="tcp")
      print(f"-- Publishing: {json.dumps(json_data)}, to Topic: {topic}, to Broker: {broker_name}.")
   except Exception as e:
        print("Error:", e)

# Callbacks
def on_publish(client, userdata, mid):
    print(f"-- Callback: Published message with mid: {str(mid)}.")

# Main
def main():
   for i in range(max_messages):
      generate_new_values()
      publish()
      time.sleep(time_delay)

if __name__ == '__main__':
   main()