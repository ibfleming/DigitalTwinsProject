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
time_delay = 1
total_status_online = 0
status = False

"""
Temperature stuff:
   - time stamp
   - room size (how much are we going to need to heat)
   - temperature outside
   - temperature inside
   - based on the temperature in the room and the temperature outside of the room, how much heat did I lose in that time stamp
      - this is essentially a tick that will run, and it will calculate every time step

   WILL NEED TO CALCULATE THE NEW STATE ON THE OLD STATE

   Need to create: tick manager - function that will call every second and will update the other finctions every second

   Need to put everything in kelvin and convert before mqtt
   get an r factor that makes sense
"""

""" This is where the temperature will be calculated """
# Constant temperature values that we need
#values in meters
ship_length = 14
ship_width = 10
ship_hieght = 3
ship_R_factor = .067

temperature_time_delay = 1       # How long between each of the temperature ticks
outside_temperature = 0.0        # This is the current temperature of the outside (surrounding the spaceship - zero as we are in space)
inside_temperature = 20.0        # This is the current temperature of the inside of the ship 
ship_surface = (ship_length * ship_width * 2) + (ship_hieght * ship_length * 2) + (ship_width * ship_hieght * 2)       # the interior of the ship will be defined as 350 meters cubed

# Returns the temperature of the ship interior
def get_interior_temperature():
   global inside_temperature
   return inside_temperature

#this will properly calculate the ship temperature
def calculate_temperature_value():
   #get the needed global values
   global outside_temperature
   global inside_temperature
   global ship_surface
   global ship_R_factor

   #Need to find the right equation to meaure this
   delta_t = (inside_temperature - outside_temperature) / ship_R_factor
   new_temperature = inside_temperature - delta_t

   print("RUNNING {}".format(new_temperature))

   inside_temperature = new_temperature



""" End of the temperature definitions """

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
   global total_status_online
   statuses = [True, False]
   updated_status = random.choice(statuses)
   if(updated_status == True):
      total_status_online += 1
   else:
      if(total_status_online > 0):
         total_status_online -= 1
   return updated_status

# Function to get the status updates (if the module is online or offline) to the connections on the antenna
def get_current_antenna_connections():
   global total_status_online
   return total_status_online

# Dictionary/JSON to be published to Broker (MQTT)
json_data = {
   "Antenna": {
         "Status": generate_random_status(),
         "Strength": generate_random_int(0, 100),
         "Connections": get_current_antenna_connections()
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
         "Value": get_interior_temperature()
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
   update_json("Antenna", "Status", True)
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
   update_json("Temperature", "Value", get_interior_temperature())

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
      if(i % 5 == 0):
         generate_new_values()
         publish()
      calculate_temperature_value()
      time.sleep(time_delay)

if __name__ == '__main__':
   main()