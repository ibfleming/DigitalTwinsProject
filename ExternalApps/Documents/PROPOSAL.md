## Design Proposal Outline for Digital Twins Project

**Goals:**
---
##### We will be developing a Digital Twin that will tell the user different readings from the place that they are located. As an example of this, if we are on a random planet then our twin will be able to model the various oxygen levels, the humidity, the temperacture, etc. of the outside world. To visualize this we will be constructing a spaceship that the user will reside in that will recieve the data from the sensors and send the data to the ship. This way the user inside the ship will be able to see if the world they are in is safe, or if it is not and can choose to go outside into the world they have landed in or they can choose to stay inside of their ship and continue to monitor the incomming data.

##### To summarize -
  - The visualization will get data on the world such as oxygen levels, humidity, temperature, etc. --- This will be both random and manual.
  - The visualization will also show data about the ship, such as fuel level and power consumption.
  - This data will simulated in Python and sent to the visualization via MQTT publisher (the visualization will subscribe).
  - The user can see the data, and choose to exit the ship or stay in the ship as they see fit.

**Objectives:**
---
##### Our objectives will be the following -
  - We will develop a virtual ship to show the world and the ship data. This will update as is happens in "real time." All of this info will be simulated with a Python script.
  - We will develop python scripts to generate data to send to the digital twin and have the displays in the twin update as they update from the script.
  - Linking the script to the ship using MQTT for subscriber to publisher communication.
  - Making interactable with the ingame player for a higher level of immersion.
  - Have animations and interactable objects in the virtual world to read the data in a better way.

**Architecture:**
---
##### We will be using Unreal Engine in order to develop the virtual simulation and have it interface with the publish/subscribe system of MQTT. We will have seperate topics that will all be sent to the same broker bus. This will work well becasue of the high output capabilities of the MQTT service. This will function better then serial becasue it doesn't have to be serial, and comes syncronized out of the box. We will then be developing some python scripts that will allow us to generate the simulated numbers before sending them to our Digital Twin that is implimented in Unreal Enreal Engine.

**Design:**
---
##### Our design will consist of the above mentioned tasks that will allow us to complete our Digital Twin to the best of our capabilities. A diagram of the flow of the design will be included below - 

![Diagram of Digital Twin](https://github.com/ibfleming/DigitalTwinsProject/blob/main/ExternalApps/Documents/Draw_io/DigitalTwinsProjectProposalDiagram.png)

---
**New Design Document:**
---

##### Edit the previous, if there are changes then edit the doc to show changes, if no changes then leave the design doc the same. 

##### If there are changes then title the doc:
- Design V1
- Design V2 (If no changes then add no changes to the bottom of this section) - if no edits then just skip this section all together - (No changes from V1) 

##### Add in a new section called DATA EXCHANGE:
- This will include the types and the frequency of the data that we will be getting
- Status updates about all of the data that we are going to be recieving from the system, and what that is going to update.
- Control actions: This is things that happen based on the "real world" part of the twin. An example of this is if I turn the lights on in the room that is being modeled, then the lights will also need to be turned on/off in the digital twin.
- Also add a priority section to this document so that we can get the order of which thing we will impliment first, ie which is most important to recieve and which is not as important to add.
