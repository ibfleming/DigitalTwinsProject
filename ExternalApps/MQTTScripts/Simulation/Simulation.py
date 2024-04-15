"""
    Simulation Manager
    Artificially produces "real-world" data and sends it over MQTT.
"""

import os
import time
import json
import random
import paho.mqtt.client as mqtt

# Topics
simulation_topic = "SimulationTopic"
pid_topic        = "PIDTopic"

# Globals
room_temp = 75.0
heater    = False

# Simulation data in JSON
sim_data = {
   "Antenna": {
         "Status": False,
         "Strength": 0,
         "Connections": 0
   },
   "ComputerSystem": {
         "Status": False,
         "Direction": "",
         "Speed": 0.0
   },
   "Engine": {
         "Status": False,
         "Temperature": 0.0,
         "Pressure": 0,
         "RPM": 0
   },
   "Thruster": {
         "Status": False,
         "Power": 0,
         "Fuel": 0
   },
   "Temperature": {
         "Status": False,
         "Value": 0.0,
         "Heater": False
   }
}

""" Callback Functions """

def connect_callback(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connected to broker.")
        # Publish PID
        print("Publishing PID.")
        client.publish(pid_topic, payload="pid" + str(os.getpid()))
        
    else:
        print("Failed to connect to broker.")

"""
def message_callback(client, userdata, msg):
    pass

def disconnect_callback(client, userdata, reason_code, properties):
    pass

def publish_callback(client, userdata, mid):
    pass

def subscribe_callback(client, userdata, mid, reason_code_list, properties):
    pass
"""

""" Functions """

def generate_new(data=sim_data):
    for key in data.keys():
        match key:
            case 'Antenna':
                data[key]["Status"]      = gen_status()
                data[key]["Strength"]    = gen_int(0, 100)
                data[key]["Connections"] = gen_int(1, 4)
            case 'ComputerSystem':
                data[key]["Status"]      = gen_status()
                data[key]["Direction"]   = gen_direction(data[key]["Direction"])
                data[key]["Speed"]       = gen_float(25, 100)
            case 'Engine':
                data[key]["Status"]      = gen_status()
                data[key]["Temperature"] = gen_float(0, 100)
                data[key]["Pressure"]    = gen_int(0, 300)
                data[key]["RPM"]         = gen_int(750, 7200)
            case 'Thruster':
                data[key]["Status"]      = gen_status()
                data[key]["Power"]       = gen_int(0, 250)
                data[key]["Fuel"]        = gen_int(0, 100)
            case 'Temperature':
                data[key]["Status"]      = gen_status()
                data[key]["Value"]       = room_temp
                data[key]["Heater"]      = heater

# Generate Random Status
def gen_status():
    return random.choice([True, False])

# Generate Random Integers
def gen_int(min, max):
    return random.randint(min, max)

# Generate Random Floats
def gen_float(min, max):
    return round(random.uniform(min, max), 1)

# Generate Random Direction
def gen_direction(curr_dir):
    match curr_dir:
        case "N":
            return random.choice(["N", "NE", "NW"])
        case "NE":
            return random.choice(["N", "NE", "E"])
        case "E":
            return random.choice(["NE", "E", "SE"])
        case "SE":
            return random.choice(["E", "SE", "S"])
        case "S":
            return random.choice(["SE", "S", "SW"])
        case "SW":
            return random.choice(["S", "SW", "W"])
        case "W":
            return random.choice(["SW", "W", "NW"])
        case "NW":
            return random.choice(["W", "NW", "N"])
        case _:
            return random.choice(["N", "NE", "E", "SE", "S", "SW", "W", "NW"])

# Generate Temperature Value
def gen_temp():

    global room_temp
    global heater

    # Ship Parameters (in meters)
    #length   = 14
    #width    = 10
    #height   = 3
    r_factor = 100
    #area     = (length * width * 2) + (height * length * 2) + (width * height * 2) 

    # Temperature Paramters
    outside_temp = 0.0

    delta  = (room_temp - outside_temp) / r_factor
    f_temp = room_temp - delta

    room_temp = round(f_temp, 1)

    if( room_temp <= 65.0 and heater is False ):
        heater = True
    
    if( heater ):
        room_temp += 1
        if( room_temp >= 72.0 ):
            heater = False

def main():

    # Client paramters
    cid  = "SimulationManager"
    host = "localhost"
    port = 1883

    # Simulation parameters
    max_messages = 1000
    time_delay   = 1

    # Create a client instance
    client = mqtt.Client(client_id=cid, protocol=mqtt.MQTTv5, transport="tcp")
    client.max_queued_messages_set   = 0
    client.max_inflight_messages_set = 0

    # Assign callbacks
    client.on_connect = connect_callback
    #client.on_disconnect = disconnect_callback
    #client.on_message = message_callback
    #client.on_publish = publish_callback
    #client.on_subscribe = subscribe_callback

    # Connect to the broker
    client.connect(host=host, port=port, keepalive=60, clean_start=True)

    try:
        client.loop_start()
        time.sleep(time_delay)

        print("Simulation initiated.\nPublishing simulation data...\n")
        for i in range(max_messages):
            gen_temp()
            generate_new()
            print(sim_data, end="\n\n")
            client.publish(simulation_topic, payload=json.dumps(sim_data))
            time.sleep(time_delay)
            
    except KeyboardInterrupt or Exception:
        client.loop_stop()
        client.disconnect()

if __name__ == '__main__':
    main()