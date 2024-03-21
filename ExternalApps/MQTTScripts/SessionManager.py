import datetime
import platform
import subprocess
import paho.mqtt.client as mqtt
import time
import uuid
import psutil


# Use Shell=True for Windows
useShell = True

# Statuses
connected = False
inSession = False

# UUID
uuid = uuid.uuid4()

# MQTT Parameters
broker_name = "localhost"
broker_port = 1883
CID = "SessionManager"

# Topics
session_topic = "SessionTopic"
uuid_topic    = "UUIDTopic"
pid_topic     = "PIDTopic"

# Script Paths
database_script = "Database/ArrowDB.py"
simulation_script = "Simulation/Simulation.py"
running_processes = [] # Stores subprocess objects
shell_pids = [] # Stores PID from shells

# Callback Functions

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker!\nAwaiting session start...\n")
        global connected
        connected = True
    else:
        print("Cannot connect to broker.")

def on_message(client, userdata, message):
    if message.topic == pid_topic:
        pid = message.payload.decode('utf-8')[3:] # Remove 'pid' from the payload, ie. 'pid1234' -> '1234'
        print(f"Received external python process. (PID: {pid})")
        shell_pids.append(int(pid))
    else:
        global inSession

        payload = message.payload.decode('utf-8')

        if not inSession:
            if payload == "Start":
                    inSession = True
                    print("Received session start request...")
                    print(f"Created new session at {datetime.datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")}.")
                    print(f"\tUUID: {uuid}\n")
                    print("Dispatching scripts...")

                    # Dispatch the scripts
                    dispatch_script(database_script)
                    dispatch_script(simulation_script)

                    print("Scripts dispatched.\n")
        elif inSession:
            if payload == "End":
                inSession = False
                print("\nReceived session stop request...")
                print(f"Ended the session at {datetime.datetime.now().strftime("%m/%d/%Y %I:%M:%S %p")}.")
                print(f"\tUUID: {uuid}\n")
                print("Terminating scripts...")
                terminate_scripts()

# Functions

def dispatch_script(script_path):
    if not useShell:
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
        print(f"\tExecuting script. (Subprocess PID: {process.pid})")

def terminate_scripts():
    if not useShell:
        # Subprocess PID and PID from Script will match always
        try:
            for process in running_processes:
                process.terminate()
                print(f"\tScript terminated successfully. (PID: {process.pid})")
            print("Scripts terminated successfully.")
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
                    print(f"\tScript terminated successfully. (cmd.exe PID: {cmd_pid}, Python PID: {shell_pids[index]})")
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess) as e:
                    print(f"Error terminating scripts: {e}")
            else:
                print("Corresponding cmd.exe process not found.")
        print("Scripts terminated successfully.")
    running_processes.clear()
    shell_pids.clear()
    print("\nAwaiting session start...\n")

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

# Main

def main():

    print("===============================")
    print("\tSession Manager\t")
    print("===============================\n")

    # Client
    client = mqtt.Client(CID)
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(broker_name, port=broker_port)
    client.loop_start()

    while not connected:
        time.sleep(0.1)

    client.subscribe(session_topic)
    client.subscribe(uuid_topic)
    client.subscribe(pid_topic)

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting...")
        client.disconnect()
        client.loop_stop()

if __name__ == "__main__":
    main()