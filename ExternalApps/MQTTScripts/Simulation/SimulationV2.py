"""
    Simulation Manager
    Artificially produces "real-world" data and sends it over MQTT.
"""

import os
import time
import json
import paho.mqtt.client as mqtt

# Topics
simulation_topic = "SimulationTopic"
pid_topic        = "PIDTopic"

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
        print("Publishing PID.", end=" ")
        client.publish(pid_topic, payload="pid" + str(os.getpid()))
    else:
        print("Failed to connect to broker.")

def message_callback(client, userdata, msg):
    pass

def disconnect_callback(client, userdata, reason_code, properties):
    pass

def publish_callback(client, userdata, mid):
    pass

def subscribe_callback(client, userdata, mid, reason_code_list, properties):
    pass

""" Functions """

def generate_new(data=sim_data):
    for key in data.keys():
        match key:
            case 'Antenna':
                data[key]["Status"] = True
                data[key]["Strength"] = 0
                data[key]["Connections"] = 0
            case 'ComputerSystem':
                data[key]["Status"] = True
                data[key]["Direction"] = ""
                data[key]["Speed"] = 0
            case 'Engine':
                data[key]["Status"] = True
                data[key]["Temperature"] = 0.0
                data[key]["Pressure"] = 0
                data[key]["RPM"] = 0
            case 'Thruster':
                data[key]["Status"] = True
                data[key]["Power"] = 0
                data[key]["Fuel"] = 0
            case 'Temperature':
                data[key]["Status"] = True
                data[key]["Value"] = 0.0
                data[key]["Heater"] = True
            case _:
                print("No!")

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
    client.on_disconnect = disconnect_callback
    client.on_message = message_callback
    client.on_publish = publish_callback
    client.on_subscribe = subscribe_callback

    # Connect to the broker
    client.connect(host=host, port=port, keepalive=60, clean_start=True)

    try:
        print("Simulation initiated.\nPublishing simulation data...\n")
        for i in range(max_messages):
            generate_new()
            client.publish(simulation_topic, payload=json.dumps(sim_data))
            print(sim_data)
            #calculate_temperature_value
            time.sleep(time_delay)
    except KeyboardInterrupt or Exception:
        client.disconnect()

if __name__ == '__main__':
    main()