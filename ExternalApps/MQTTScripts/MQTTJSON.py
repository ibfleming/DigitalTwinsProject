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

""" This is where the temperature will be calculated """
# Constant temperature values that we need
#values in meters
ship_length = 14
ship_width = 10
ship_hieght = 3
ship_R_factor = 100              # We need a very big R factor so se don't loose too much heat every second
heat_is_on = False               # Keep track of if the temperature is on or not

temperature_time_delay = 1       # How long between each of the temperature ticks
outside_temperature = 0.0        # This is the current temperature of the outside (surrounding the spaceship - zero as we are in space)
inside_temperature = 75.0        # This is the current temperature of the inside of the ship 
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
   global heat_is_on

   delta_t = (inside_temperature - outside_temperature) / ship_R_factor
   new_temperature = inside_temperature - delta_t

   #print("RUNNING {}".format(new_temperature))

   inside_temperature = round(new_temperature, 3)

   # Turn on the heat if the ship is too cold
   if(inside_temperature <= 65.0 and heat_is_on == False):
      heat_is_on = True
   
   if(heat_is_on == True):
      inside_temperature += 1
      if(inside_temperature >= 80):
         heat_is_on = False

# This returns if the heater is currently enabled or not, for the enabling of the VFX
def get_heater_on():
   global heat_is_on
   return heat_is_on

""" ---------------------------- End of the temperature definitions  ---------------------------------------------- """

# Function to generate a random integer within a given range
def generate_random_int(min_value, max_value):
    return random.randint(min_value, max_value)

# Function to generate a random float within a given range
def generate_random_float(min_value, max_value):
    return round(random.uniform(min_value, max_value), 1)

""" -- Ship direction functions to get the proper direction the ship is going in -- """

current_ship_direction = "N"

def get_current_ship_direction():
   global current_ship_direction
   current_ship_direction = generate_random_direction()

   #print("CURRENT SHIP DIRECTION: {}".format(current_ship_direction))

   return current_ship_direction

# Function to choose a random direction (based on the current direction that the ship is oriented in)
def generate_random_direction():
   global current_ship_direction
   # These are the possible directions that the ship is able to head out in
   directions = ["N", "NW", "S", "SW", "E", "W", "SE", "NE"]

   match current_ship_direction:
      case "N":
         return random.choice(["NE", "NW"])
      case "NE":
         return random.choice(["N", "E"])
      case "E":
         return random.choice(["NE", "SE"])
      case "SE":
         return random.choice(["E", "S"])
      case "S":
         return random.choice(["SE", "SW"])
      case "SW":
         return random.choice(["S", "W"])
      case "W":
         return random.choice(["SW", "NW"])
      case "NW": 
         return random.choice(["N", "W"])
      case default:
         # Randomly choose is all else fails
         return random.choice(directions)   

""" ---------------------- End of the ship direction functions --------------------------- """

""" Status Module Functions - These will be enabled and online unless they are forably disabled by something breaking """
# This will turn the module on by default
def generate_online_status():
   global total_status_online
   updated_status = True
   if(updated_status == True):
      total_status_online += 1
   else:
      if(total_status_online > 0):
         total_status_online -= 1
   return updated_status

# This will turn the module off, can be called to disable the working status under certain conditions
def generate_offline_status():
   global total_status_online
   updated_status = False
   if(updated_status == True):
      total_status_online += 1
   else:
      if(total_status_online > 0):
         total_status_online -= 1
   return updated_status

# This generates the end of the random value of the modules going online or offline, will be used when there is a seeable system failure
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

""" ------------------------------ End of Status functions ------------------------------------------- """

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
         "Direction": get_current_ship_direction(),
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
         "Value": get_interior_temperature(),
         "Heater": get_heater_on()
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
   update_json("Antenna", "Status", generate_online_status())
   update_json("Antenna", "Strength", generate_random_int(0, 100))
   update_json("Antenna", "Connections", generate_random_int(1, 10))
   # Computer System
   update_json("ComputerSystem", "Status", generate_online_status())
   update_json("ComputerSystem", "Direction", get_current_ship_direction())
   update_json("ComputerSystem", "Speed", generate_random_float(25, 100))
   # Engine
   update_json("Engine", "Status", generate_online_status())
   update_json("Engine", "Temperature", generate_random_float(-10, 72))
   update_json("Engine", "Pressure", generate_random_int(0, 100))
   update_json("Engine", "RPM", generate_random_int(500, 7200))
   # Thruster
   update_json("Thruster", "Status", generate_online_status())
   update_json("Thruster", "Power", generate_random_int(0, 100))
   update_json("Thruster", "Fuel", generate_random_int(0, 100))
   #Temperature
   update_json("Temperature", "Status", generate_online_status())
   update_json("Temperature", "Value", get_interior_temperature())
   update_json("Temperature", "Heater", get_heater_on())

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