<img src="https://github.com/ibfleming/digital-twins/blob/main/ExternalApps/Media/spaceship.png" alt="spaceship"/>

# Skeletor in Space - Digital Twins Project

**Authors:** Ian Fleming and Lucien Lee

Welcome to the Skeletor in Space project repository! This is where we've centralized all the code and resources for our Digital Twins endeavor, undertaken as part of the CS404 course instructed by Dr. Conte de Leon at the University of Idaho during the Spring 2024 semester.

## Table of Contents
- [Overview](#overview)
- [Video Demonstration](#video-demonstration)
- [Usage](#usage)
  - [Cloning the Repository](#cloning-the-repository)
  - [Opening the Project](#opening-the-project)
  - [Ensure MQTT is Installed](#ensure-mqtt-is-installed)
  - [Ensure Python is Installed](#ensure-python-is-installed)
  - [Testing and Simulating the Environment](#testing-and-simulating-the-environment)
- [Contact](#contact)
- [License](#license)

## Overview

Welcome to the Skeletor in Space project repository! This project aims to explore the concept of digital twins in the context of a spaceship in space. Leveraging Unreal Engine 5.3, we utilize both 3D and 2D assets to create immersive visualizations of our digital twin model.

To enhance our data visualization capabilities, we employ charting plugins such as Kantan Charts within the Unreal Engine environment. These charts help us analyze and interpret complex data sets effectively.

For networking and real-time data exchange between the server and client, we implement the MQTT (mosquitto) publisher/subscriber model. This allows seamless communication and the transfer of data encoded in JSON format, ensuring efficient data synchronization and interaction.

To simulate realistic scenarios and generate mock data, we integrate Python scripts into our workflow. These scripts enable us to simulate various environmental conditions and events, providing valuable insights into the behavior of our digital twin.

Furthermore, to manage and store historical data efficiently, we utilize PyArrow parquet to store older data into a database. This ensures that past data remains accessible for analysis and comparison, contributing to the ongoing refinement and improvement of our digital twin model.

In summary, these are our primary components and resources we utilized in order to achieve a minimal viable product.

## Video Demonstration

[Demo](https://github.com/ibfleming/digital-twins/blob/main/ExternalApps/Media/FinalDemoVideo.mkv)

## Usage

Ensure all the actions under each section have been completed to ensure the project to work.

### Cloning the Repository

To clone the repository to your local environment, use the following command:

```bash
git clone https://github.com/ibfleming/digital-twins.git
```

### Opening the Project

Ensure you have Unreal Engine 5.3 installed and working on your local machine from the Epic Games Launcher.
You can open up the project in Unreal by opening the ```.uproject``` file in the root directory of the repository.
You might be required to generate project files beforehand.

### Ensure MQTT is Installed

Your machine will require the background process, ```mosquitto.exe``` to be running in order for all MQTT implementations within the Unreal Engine project
and scripts to work accordingly. You can download and install the application [here](https://mosquitto.org/download/). 

### Ensure Python is Installed

Your machine will require the latest version of Python installed on your local machine to enable the compilation and execution of Python scripts.
Our scripts also use custom packages that you must download and install over ```pip``` or some other package manager in order for them to compile successfully.

Here are the packages in question (this may not be a complete list, so observe what packages are missing based on the compilation errors):
- paho-mqtt
- pyarrow
- pandas

### Testing and Simulating the Environment

Before running the simulation in Unreal, ensure the ```SessionManager.py``` script is running in the background located in the ```ExternalApps/Scripts``` directory.

To execute the script:
```bash
python SessionManager.py
```

Now, feel free to simulate the environment in Unreal testing out the terminals, hologram emitter, and various components of the spaceship.

Have fun and thanks for visiting the repository!

## Contact

For questions or concerns, use this e-mail: ```ianfleming678@gmail.com```

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
