import spotipy
import sys
import os
import datetime
import time
import json
from spotipy.oauth2 import SpotifyOAuth

class Alarm:
    def __init__(self):
        #variable for user set wake up time
        self.wakeUpTime = "09:00:00"
        #variable for spotipy PC player id
        self.deviceId = ""
        #spotifpy config and spotify authentication so we can control spotify using API
        self.sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id="",
                                                client_secret="",
                                                redirect_uri="https://localhost:8008",
                                                scope="user-modify-playback-state user-read-playback-state"))

    def setWakeUpTime(self, requestTime):
        self.wakeUpTime = requestTime

    def waitForWakeUp(self):
        alarm_hour = self.wakeUpTime[0:2]
        alarm_minute = self.wakeUpTime[3:5]
        alarm_seconds = self.wakeUpTime[6:8]

        print("Alarm set for: " + alarm_hour + ":" + alarm_minute + ":" + alarm_seconds)

        now = datetime.datetime.utcnow()+datetime.timedelta(hours=(-4))
        set_hour = now.strftime("%H")
        set_minute = now.strftime("%M")
        set_seconds = now.strftime("%S")
        print("Current Time: " + set_hour + ":" + set_minute + ":" + set_seconds)
        
        print("Alarm pending, waiting for trigger time...")
        sys.stdout.flush()
        
        while True:
            now = datetime.datetime.utcnow()+datetime.timedelta(hours=(-4))
            current_hour = now.strftime("%H")
            current_minute = now.strftime("%M")
            current_seconds = now.strftime("%S")
            if(alarm_hour==current_hour):
                if(alarm_minute==current_minute):
                    if(alarm_seconds==current_seconds):
                        print("Wake Up!")
                        sys.stdout.flush()
                        self.turnOnRoom()
                        self.verifyPCAvailability()
                        break

            alarm_set = True
            with open('globals.json', 'r+') as f:
                data = json.load(f)
                if (data['alarm_set'] == 0):
                    alarm_set = False
            if(alarm_set == False):
                print("*Alarm Cancelled*")
                sys.stdout.flush()
                break

    def turnOnRoom(self):

        with open('globals.json', 'r+') as f:
            data = json.load(f)
            data['room_status'] = 1
            data['alarm_triggered'] = 1
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()

        print("Turning on Devices...")
        #runs command to turn on speaker
        os.system('irsend SEND_ONCE EDIFIER KEY_POWER')
        time.sleep(1)

        #runs command to turn on tv
        os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A_POWER KEY_POWER')
        time.sleep(1)

        #runs command to wake computer
        os.system('sudo etherwake -i eth0 "MAC ADDRESS"')

        #turns brightness of tv down
        time.sleep(20)
        #IR code sequence to lower brightness of TV
        os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A KEY_MENU')
        time.sleep(2)
        os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A KEY_RIGHT')
        time.sleep(1)
        os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A KEY_DOWN')
        time.sleep(1)
        os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A KEY_SELECT')
        time.sleep(3)
        os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A KEY_LEFT')
        time.sleep(1)
        os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A KEY_LEFT')
        time.sleep(1)
        os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A KEY_LEFT')
        time.sleep(1)
        os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A KEY_LEFT')
        time.sleep(1)
        os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A KEY_LEFT')
        time.sleep(1)
        os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A KEY_EXIT')
        return

    def verifyComputerAwake(self):
        #check to see if PC can play spotify, if not, then move to emergency protocol
        count = 0
        BEAST_AVAILABLE = False
        while(BEAST_AVAILABLE == False):
            #Checking for available devices
            devices = self.sp.devices()
            device_names = [None] * len(devices['devices'])
            device_identification = [None] * len(devices['devices'])
            print(devices['devices'])
            for i in range(len(devices['devices'])):
                device_names[i] = devices['devices'][i]['name']
                device_identification[i] = devices['devices'][i]['id']


            #Check to see if spotify is open on PC
            for i in range(len(device_names)):
                if (device_names[i] == "BEAST"):
                    BEAST_AVAILABLE = True
                    self.deviceId = device_identification[i]
                    self.startMusic()

            #Failure after ~5 minutes of checking, else wait 
            #5 seconds before next check
            if (count > 60):
                BEAST_AVAILABLE = True
                print("MAXIMUM CHECK REACHED")
                print("Moving to Emergency protocol...")
            else:
                count = count + 1
                time.sleep(5)
                print("PC Not Available: Check " + str(count) + "/60")

    #Plays alarm clock playist on spotify on PC and logarithmically raises volume
    def startMusic(self):
        print('**Now playing "Alarm Clock" playlist on PC**')
        alarm_set = True
        # pause to wait for PC spotify to be ready
        time.sleep(90)
        # Set volume to 25 and play wake up spotify playist on PC
        volume_percent = 25
        self.sp.volume(volume_percent, device_id=self.deviceId)
        self.sp.shuffle(True, device_id=self.deviceId)
        self.sp.start_playback(device_id=self.deviceId, context_uri='spotify:playlist:"PLAYLIST_URI"', uris=None, offset=None, position_ms=None)

        time.sleep(60)

        with open('globals.json', 'r+') as f:
                data = json.load(f)
                if (data['snooze_set'] == 1):
                    alarm_set = False
        if (alarm_set == False):
            print("*Alarm Cancelled*")
            return

        volume_percent = 30
        self.sp.volume(volume_percent, device_id=self.deviceId)
            
        time.sleep(120)

        #Gradually raise volume from 30-40
        for i in range(3):
            with open('globals.json', 'r+') as f:
                data = json.load(f)
                if (data['snooze_set'] == 1):
                    alarm_set = False
            if (alarm_set == False):
                print("*Alarm Cancelled*")
                return
            volume_percent = 30 + 5*i
            self.sp.volume(volume_percent, device_id=self.deviceId)
            print("Volume " + str(volume_percent) +"%")
            time.sleep(60)

        time.sleep(180)

        #Gradually raise volume from 40-60
        for i in range(5):
            with open('globals.json', 'r+') as f:
                data = json.load(f)
                if (data['alarm_set'] == 0 or data['snooze_set'] == 1):
                    alarm_set = False
            if (alarm_set == False):
                print("*Alarm Cancelled*")
                return
            volume_percent = 40 + 5*i
            self.sp.volume(volume_percent, device_id=self.deviceId)
            print("Volume " + str(volume_percent) +"%")
            time.sleep(30)

        time.sleep(120)

        with open('globals.json', 'r+') as f:
                data = json.load(f)
                if (data['alarm_set'] == 0 or data['snooze_set'] == 1):
                    alarm_set = False
        if (alarm_set == False):
            print("*Alarm Cancelled*")
            return

        print("WARNING: critical volume levels approaching")

        #Gradually raise volume from 60-80
        for i in range(3):
            with open('globals.json', 'r+') as f:
                data = json.load(f)
                if (data['alarm_set'] == 0 or data['snooze_set'] == 1):
                    alarm_set = False
            if (alarm_set == False):
                print("*Alarm Cancelled*")
                return
            volume_percent = 60 + 10*i
            self.sp.volume(volume_percent, device_id=self.deviceId)
            print("Volume " + str(volume_percent) +"%")
            time.sleep(60)

        time.sleep(120)

        with open('globals.json', 'r+') as f:
                data = json.load(f)
                if (data['alarm_set'] == 0 or data['snooze_set'] == 1):
                    alarm_set = False
        if (alarm_set == False):
            print("*Alarm Cancelled*")
            return
        
        print("DANGEROUS VOLUME LEVELS: Mom might get pissed!")
        
        #Gradually raise volume from 80-100
        for i in range(3):
            with open('globals.json', 'r+') as f:
                data = json.load(f)
                if (data['alarm_set'] == 0 or data['snooze_set'] == 1):
                    alarm_set = False
            if (alarm_set == False):
                print("*Alarm Cancelled*")
                return
            volume_percent = 80 + 10*i
            self.sp.volume(volume_percent, device_id=self.deviceId)
            print("*DANGER* Volume " + str(volume_percent) +"%")
            time.sleep(120)
        
        print("***Alarm Ending***")

    def snooze(self):
        #pauses the music
        try:
            self.sp.pause_playback(device_id=self.deviceId)
        except:
            print("Tried pausing already paused music, IDIOT!")

        alarm_hour = self.wakeUpTime[0:2]
        alarm_minute = self.wakeUpTime[3:5]
        alarm_seconds = self.wakeUpTime[6:8]

        print("Alarm set for: " + alarm_hour + ":" + alarm_minute + ":" + alarm_seconds)

        now = datetime.datetime.utcnow()+datetime.timedelta(hours=(-4))
        set_hour = now.strftime("%H")
        set_minute = now.strftime("%M")
        set_seconds = now.strftime("%S")
        print("Current Time: " + set_hour + ":" + set_minute + ":" + set_seconds)
        
        print("Alarm pending, waiting for trigger time...")
        
        while True:
            now = datetime.datetime.utcnow()+datetime.timedelta(hours=(-4))
            current_hour = now.strftime("%H")
            current_minute = now.strftime("%M")
            current_seconds = now.strftime("%S")
            if(alarm_hour==current_hour):
                if(alarm_minute==current_minute):
                    if(alarm_seconds==current_seconds):
                        print("Wake Up!")
                        print('**Now playing "Alarm Clock" playlist on PC**')
                        #unset snooze once triggered so that new snooze can be activated
                        with open('globals.json', 'r+') as f:
                            data = json.load(f)
                            data['snooze_set'] = 0
                            f.seek(0)
                            json.dump(data, f, indent=4)
                            f.truncate()
                        alarm_set = True
                        # Set volume to 25 and play wake up spotify playist on PC
                        volume_percent = 25
                        self.sp.volume(volume_percent, device_id=self.deviceId)
                        self.sp.shuffle(True, device_id=self.deviceId)
                        self.sp.start_playback(device_id=self.deviceId, context_uri='spotify:playlist:"PLAYLIST_URI"', uris=None, offset=None, position_ms=None)

                        time.sleep(60)

                        with open('globals.json', 'r+') as f:
                                data = json.load(f)
                                if (data['snooze_set'] == 1):
                                    alarm_set = False
                        if (alarm_set == False):
                            print("*Alarm Cancelled*")
                            return

                        volume_percent = 30
                        self.sp.volume(volume_percent, device_id=self.deviceId)
                            
                        time.sleep(120)

                        #Gradually raise volume from 30-40
                        for i in range(3):
                            with open('globals.json', 'r+') as f:
                                data = json.load(f)
                                if (data['snooze_set'] == 1):
                                    alarm_set = False
                            if (alarm_set == False):
                                print("*Alarm Cancelled*")
                                return
                            volume_percent = 30 + 5*i
                            self.sp.volume(volume_percent, device_id=self.deviceId)
                            print("Volume " + str(volume_percent) +"%")
                            time.sleep(60)

                        time.sleep(180)

                        #Gradually raise volume from 40-60
                        for i in range(5):
                            with open('globals.json', 'r+') as f:
                                data = json.load(f)
                                if (data['alarm_set'] == 0 or data['snooze_set'] == 1):
                                    alarm_set = False
                            if (alarm_set == False):
                                print("*Alarm Cancelled*")
                                return
                            volume_percent = 40 + 5*i
                            self.sp.volume(volume_percent, device_id=self.deviceId)
                            print("Volume " + str(volume_percent) +"%")
                            time.sleep(30)

                        time.sleep(120)

                        with open('globals.json', 'r+') as f:
                                data = json.load(f)
                                if (data['alarm_set'] == 0 or data['snooze_set'] == 1):
                                    alarm_set = False
                        if (alarm_set == False):
                            print("*Alarm Cancelled*")
                            return

                        print("WARNING: critical volume levels approaching")

                        #Gradually raise volume from 60-80
                        for i in range(3):
                            with open('globals.json', 'r+') as f:
                                data = json.load(f)
                                if (data['alarm_set'] == 0 or data['snooze_set'] == 1):
                                    alarm_set = False
                            if (alarm_set == False):
                                print("*Alarm Cancelled*")
                                return
                            volume_percent = 60 + 10*i
                            self.sp.volume(volume_percent, device_id=self.deviceId)
                            print("Volume " + str(volume_percent) +"%")
                            time.sleep(60)

                        time.sleep(120)

                        with open('globals.json', 'r+') as f:
                                data = json.load(f)
                                if (data['alarm_set'] == 0 or data['snooze_set'] == 1):
                                    alarm_set = False
                        if (alarm_set == False):
                            print("*Alarm Cancelled*")
                            return
                        
                        print("DANGEROUS VOLUME LEVELS: Mom might get pissed!")
                        
                        #Gradually raise volume from 80-100
                        for i in range(3):
                            with open('globals.json', 'r+') as f:
                                data = json.load(f)
                                if (data['alarm_set'] == 0 or data['snooze_set'] == 1):
                                    alarm_set = False
                            if (alarm_set == False):
                                print("*Alarm Cancelled*")
                                return
                            volume_percent = 80 + 10*i
                            self.sp.volume(volume_percent, device_id=self.deviceId)
                            print("*DANGER* Volume " + str(volume_percent) +"%")
                            time.sleep(120)
                        
                        print("***Alarm Ending***")
                        break

            alarm_set = True
            with open('globals.json', 'r+') as f:
                data = json.load(f)
                if (data['alarm_set'] == 0):
                    alarm_set = False
            if(alarm_set == False):
                print("*Alarm Cancelled*")
                break




