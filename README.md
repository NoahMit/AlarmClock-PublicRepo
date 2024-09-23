# Custom RPI Based Alarm Clock
There is not much I dislike more than alarm clocks. It seems as though the only options out there are annoying songs being played out of tinny speakers, and who wants to be annoyed by this the moment they wake up. So, I decided to take into my own hands and create an alarm clock that provides a more delightful awakening. To achieve this I set some simple requirements: <br />
- Alarm sound must be randomly selected songs from a premade playlist
- Volume must gradually increase
- Good quality speakers
- Web App to set the Alarm


A few other useful features were added including a snooze button and a count down timer.
# Hardware Diagram
<p align="center">
  <img src="https://github.com/NoahMit/AlarmClock/blob/master/hardware%20diagram.png?raw=true" alt="Sublime's custom image"/>
</p>
<br />

# Web App
<p align="center">
  <img src="https://github.com/NoahMit/AlarmClock/blob/master/frontend%20demo.gif?raw=true" alt="Sublime's custom image"/>
</p>
<br />
<p align="center">
  <img src="https://github.com/NoahMit/AlarmClock/blob/master/functionality%20diagram.png?raw=true" alt="Sublime's custom image"/>
</p>
<br />

## turn_on_room.py
First the RPI sends IR signals to turn ON the TV and the speakers via the Linux Infrared Remote Control (LIRC) package. Then, the RPI will turn ON the PC via the ethernet cable connecting the two computers by using a WakeOnLan command.

## turn_off_room.py
First the RPI sends IR signals to turn OFF the TV and the speakers via the Linux Infrared Remote Control (LIRC) package. Then, the RPI will turn OFF the PC via a Linux Samba-Common package command and WIndows' Remote Shut Down.

## Alarm.py
<ins>**DATA ATTRIBUTES**</ins>
<br />
<br />
***self.wakeUpTime***: Stores the target time that will trigger the alarm.
<br />
<br />
***self.deviceId***: Stores the Spotify API device ID of the PC  
<br />
***self.sp***: Variable used to interface with the Spotify API. It is initialized using the Spoti**py** Python library and authentication is done inline upon initialization of the data attribute.
<br />
<br />
<ins>**METHODS**</ins>
<br />
<br />
***setWakeUpTime()***: Allows api.py to set the wakeUpTime data attribute of an Alarm object.
<br />
<br />
***waitForWakeUp()***: Method will initially get hung up in a while loop that retrieves the current time and compares it to the wakeUpTime. At the end of each loop, the method will also check the "alarm_set" variable found in globals.json to verify that the alarm is still set. If the alarm is no longer set the method will break from the while loop, cancelling the alarm. If the alarm is never cancelled, the method will invoke the turnOnRoom() method as well as the verifyPCAvailability() method once the current time and wakeUpTime match and then will break from the loop.
<br />
<br />
***turnOnRoom()***: This method will first set both the variables room_status and alarm_triggered found in globals.json to 1 (True). It will then follow the same sequence of sending IR codes and a WakeOnLan command as found in turn_on_room.py. 
<br />
<br />
***verifyPCAvailability()***: Every 5 seconds this method will check to see if the PC is found in the list of available devices returned by the Spotify API. It will do a total of 60 checks in case of any errors causing an endless loop. The method will terminate if the PC is not available after 60 tries, but the alarm wont be cancelled. If the PC is found in the list of devices, the deviceId data attribute will be given the value returned by the Spotify API, then the startMusic() method will be called and lastly, the method will break from the loop. 
<br />
<br />
***startMusic()***: This method starts with a delay to make sure the Spotify app has fully launched on the PC. It will then start playing music from a specific playlist on the Spotify account, gradually increasing the volume over time. Once the method reaches maximum volume, it terminates. There is an issue with this method, however, when trying to snooze the alarm. This is due to the fact that snoozing creates a new Alarm object, and the current Alarm object will continue to increase the volume if not cancelled. To solve this, before each volume increase this method must check the "snooze_set" variable found in globals.json and if it is set, the method will terminate.
<br />
<br />
***snooze()***: This method is almost identical to the waitForWakeUp(), except when the current time and wakeUpTime match, it will not execute the turnOnRoom() and verifyPCAvailability() methods. Instead it will change the "snooze_set" variable found in globals.json to 0 (False) and then execute the same code as startMusic().

# Update on the Project
## Home Assistant OS
Despite this being a great learning experience, I have since discovered [Home Assistant OS](https://www.home-assistant.io/) and migrated all functionality to this platform. This was ultimately a good decision since it not only has great community support and customizability, but also makes for easier integration and expandability. One such example is the use of the [ESPHome](https://esphome.io/index.html) add-on and an ESP32 microcontroller to control the IR blaster board over wifi. In fact, the ESP32 microcontroller can be seen in the hardware diagram!
## Custom Designed Motorized Blind Open/Closer
I also created a CAD of a "motorized blind open and closer" which functions using DC motors and a timing belt. Design has yet to be practically tested, but all compponents are based off of locally available hardware and the housing was also designed with 3D printing in mind. [Click Here] to view more about this project!
