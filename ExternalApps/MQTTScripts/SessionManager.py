"""
    Session Manager v2.0 (based on original SessionManagerV1.py)
"""

import uuid
import psutil
import datetime
import platform
import subprocess
import paho.mqtt.client as mqtt

""" Global Variables """

# Option
use_shell  = True # True = use seperate terminal windows (cmd) in Windows systems

# Status
in_session = False

# UUID
session_id = None

# Paths
database_script   = "Database/DatabaseManager.py"
simulation_script = "Simulation/Simulation.py"
replay_script     = "Replay/ReplayManager.py"

# Topics
session_topic = "SessionTopic"
uuid_topic    = "UUIDTopic"
pid_topic     = "PIDTopic"

# Arrays
running_processes = [] # Stores subprocess objects
shell_pids        = [] # Stores PID from shells

""" Callback Functions """

def connect_callback(client, userdata, flags, reason_code, properties):
    if reason_code == 0:
        print("Connected to broker.")
        # Subscribe to Topics
        client.subscribe(session_topic)
        client.subscribe(pid_topic)
    else:
        print("Failed to connect to broker.")

def message_callback(client, userdata, msg):

    message = msg.payload.decode('utf-8')
    topic = msg.topic

    if topic == session_topic:
        global in_session
        global sesssion_id

        if not in_session:
            if message == "Start":
                in_session = True
                session_id = str(uuid.uuid4())

                print()
                print("-" *  50)
                print("New Session Created:")
                print(f"   Date: {datetime.datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")}")
                print(f"   UUID: {session_id}")
                print("-" *  50)
                print()

                dispatch_script(replay_script)
                dispatch_script(database_script)
                dispatch_script(simulation_script)

                print("Publishing session UUID.")
                client.publish(uuid_topic, session_id)
            return
        if message == "End":
            print("\nCurrent session ended.")
            in_session = False
            terminate_scripts()
            return            
        return
    if topic == pid_topic:
        shell_pids.append(int(message[3:])) # Removes 'pid:' from msg and uses the sent PID
        return
    
def disconnect_callback(client, userdata, reason_code, properties):
    if reason_code == 0:
        print("Disconnected from broker.")
    else:
        print("Failed to disconnect from broker.")

def publish_callback(client, userdata, mid):
    #print(f"Message published. (mid = {mid})")
    return

def subscribe_callback(client, userdata, mid, reason_code_list, properties):
    if reason_code_list[0] == 0:
        print(f"Subscribed to topic. (mid = {mid})")
    else:
        print(f"Failed to subscribe topic. (mid = {mid})")

""" Functions """

def dispatch_script(script_path):
    if not use_shell:
        try:
            process = subprocess.Popen(['python', script_path], shell=False)
        except subprocess.CalledProcessError as e:
            print(f"Error executing script: {e}")
    else:
        try:
            if platform.system() == "Windows":
                process = subprocess.Popen(['start', 'cmd', '/k', 'python', script_path], shell=True)
        except subprocess.CalledProcessError as e:
            print(f"Error executing script: {e}")
    if process:        
        running_processes.append(process)
        print(f"Executing '{script_path}'. (Subprocess PID: {process.pid})")

def terminate_scripts():
    if not use_shell:
        # Subprocess PID and PID from Script will match always
        try:
            for process in running_processes:
                process.terminate()
                print(f"Script terminated successfully. (PID: {process.pid})")
        except Exception as e:
            print(f"Error terminating scripts: {e}")
    else:
        # Need External Python Process PID and cmd.exe PID
        for index, process in enumerate(running_processes):
            """
            Find the cmd.exe process that is running the python script and store it in cmd_pid.
            If valid, terminate the cmd.exe process and the python process from the corresponding index of shell_pids.
            """
            cmd_pid = get_cmd_pid_of_python_subprocess(process.args[4])
            if cmd_pid:
                try:
                    psutil.Process(cmd_pid).terminate()
                    psutil.Process(shell_pids[index]).terminate()
                    print(f"Script terminated successfully. (cmd.exe PID: {cmd_pid}, Python PID: {shell_pids[index]})")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                    print(f"Error terminating scripts: {e}")
            else:
                print("Corresponding cmd.exe process not found.")
    running_processes.clear()
    shell_pids.clear()

def get_cmd_pid_of_python_subprocess(script_path):
    # Iterate over all running processes
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            # Check if the process is cmd.exe
            if proc.name() == 'cmd.exe':
                # Check if the command line contains 'python' and the script name
                if 'python' in proc.cmdline() and script_path in proc.cmdline():
                    # Check if the process has a child process
                    children = proc.children(recursive=False)
                    if children:
                        # Return the PID of the cmd.exe process
                        return proc.pid
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
            print(f"Error terminating scripts: {e}")
    return None

""" Main Function """

def main():

    # Client parameters
    cid  = "SessionManager"
    host = "localhost"
    port = 1883

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
        print("Session Manager is running.")
        client.loop_forever()
    except KeyboardInterrupt or Exception:
        client.disconnect()

if __name__ == "__main__":
    main()