from Alarm import Alarm
import os
import json
import datetime
import time
from flask import Flask, request, g

app = Flask(__name__)

@app.route('/setalarmclock', methods=['GET', 'POST'])
def set_alarm_clock():
    alarm_set = False
    time_set = False
    with open('globals.json', 'r+') as f:
        data = json.load(f)
        if (data['alarm_set'] == 1):
            alarm_set = True
        if (data['wake_up_time'] != "null"):
            time_set = True
    
    if (alarm_set == True):
        if(time_set == False):
            response = ["POST unsuccessful: alarm already set, but no time set?"]
            response = json.dumps(response)
            return response
        # Case handling if the PI has been rebooted
        else:
            wake_up_time = ""
            alarm_set = False
            with open('globals.json', 'r+') as f:
                data = json.load(f)
                wake_up_time = data['wake_up_time']

            alarm = Alarm()
            alarm.setWakeUpTime(wake_up_time)
            alarm.waitForWakeUp()

            response = ["Pi Reboot alarm handling successful"]
            response = json.dumps(response)
            return response
    else:
        alarm = Alarm()
        content =  request.get_json()
        wake_up_datetime = datetime.datetime(2,2,2, int(content['time'][11:13]), int(content['time'][14:16]), int(content['time'][17:19])) + datetime.timedelta(hours=(-4))
        wake_up_time = str(wake_up_datetime.time())
        with open('globals.json', 'r+') as f:
            data = json.load(f)
            data['alarm_set'] = 1
            data['wake_up_time'] = wake_up_time
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
        alarm.setWakeUpTime(wake_up_time)
        alarm.waitForWakeUp()
        response = ["Alarm trigger/cancel successful"]
        response = json.dumps(response)
        
        return response

@app.route('/alarmstatus', methods=['GET', 'POST'])
def alarm_clock_status():
    alarm_set = False
    room_status = False
    trigger_status = False
    with open('globals.json', 'r+') as f:
        data = json.load(f)
        if (data['alarm_set'] == 1):
            alarm_set = True
        if (data['room_status'] == 1):
            room_status = True
        if (data['alarm_triggered'] == 1):
            trigger_status = True
    
    if (alarm_set == True and room_status == True and trigger_status == True):
        return {'status': 'true', 'room': 'true', 'trigger': 'true'}
    elif (alarm_set == False and room_status == True and trigger_status == True):
        return {'status': 'false', 'room': 'true', 'trigger': 'true'}
    elif (alarm_set == True and room_status == False and trigger_status == True):
        return {'status': 'true', 'room': 'false', 'trigger': 'true'}
    elif(alarm_set == False and room_status == False and trigger_status == True):
        return {'status': 'false', 'room': 'false', 'trigger': 'true'}
    elif (alarm_set == True and room_status == True and trigger_status == False):
        return {'status': 'true', 'room': 'true', 'trigger': 'false'}
    elif (alarm_set == False and room_status == True and trigger_status == False):
        return {'status': 'false', 'room': 'true', 'trigger': 'false'}
    elif (alarm_set == True and room_status == False and trigger_status == False):
        return {'status': 'true', 'room': 'false', 'trigger': 'false'}
    else:
        return {'status': 'false', 'room': 'false', 'trigger': 'false'}

@app.route('/alarmcancel', methods=['GET', 'POST'])
def alarm_clock_cancel():
    alarm_triggered = 0
    with open('globals.json', 'r+') as f:
        data = json.load(f)
        data['alarm_set'] = 0
        data['wake_up_time'] = "null"
        data['snooze_set'] = 0
        alarm_triggered = data['alarm_triggered']
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()
    if (alarm_triggered == 1):
        #IR code sequence to raise brightness of TV
        os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A KEY_MENU')
        time.sleep(2)
        os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A KEY_RIGHT')
        time.sleep(1)
        os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A KEY_DOWN')
        time.sleep(1)
        os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A KEY_SELECT')
        time.sleep(1)
        os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A KEY_RIGHT')
        time.sleep(1)
        os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A KEY_RIGHT')
        time.sleep(1)
        os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A KEY_RIGHT')
        time.sleep(1)
        os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A KEY_RIGHT')
        time.sleep(1)
        os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A KEY_RIGHT')
        time.sleep(1)
        os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A KEY_EXIT')
        with open('globals.json', 'r+') as f:
            data = json.load(f)
            data['alarm_triggered'] = 0
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()   
    return {'response' : 'Alarm Successfully Cancelled'}

    
@app.route('/roomcontrol', methods=['GET', 'POST'])
def room_control():
    room_status = False
    with open('globals.json', 'r+') as f:
        data = json.load(f)
        if (data['room_status'] == 0):
            os.system('python3 turn_on_room.py')
            data['room_status'] = 1
            room_status = True
        elif (data['room_status'] == 1):
            if (data['alarm_set'] == 1 and data['alarm_triggered'] == 1):
                data['alarm_set'] = 0
                data['wake_up_time'] = "null"
                data['alarm_triggered'] = 0
                data['snooze_set'] = 0
                #IR code sequence to raise brightness of TV
                os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A KEY_MENU')
                time.sleep(2)
                os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A KEY_RIGHT')
                time.sleep(1)
                os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A KEY_DOWN')
                time.sleep(1)
                os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A KEY_SELECT')
                time.sleep(1)
                os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A KEY_RIGHT')
                time.sleep(1)
                os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A KEY_RIGHT')
                time.sleep(1)
                os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A KEY_RIGHT')
                time.sleep(1)
                os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A KEY_RIGHT')
                time.sleep(1)
                os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A KEY_RIGHT')
                time.sleep(1)
                os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A KEY_EXIT')
            os.system('python3 turn_off_room.py')
            data['room_status'] = 0
            room_status = False
        f.seek(0)
        json.dump(data, f, indent=4)
        f.truncate()
    if(room_status == True):
        return {'response' : 'Room Status: On'}
    else:
        return {'response' : 'Room Status: Off'}

@app.route('/getwakeuptime', methods=['GET', 'POST'])
def return_wake_up_time():
    with open('globals.json', 'r+') as f:
        data = json.load(f)
        time = data['wake_up_time']
    return {'time' : time}

@app.route('/alarmpause', methods=['GET', 'POST'])
def alarm_snooze():
    snooze_set = False
    with open('globals.json', 'r+') as f:
        data = json.load(f)
        if (data['snooze_set'] == 1):
            snooze_set = True
    
    if (snooze_set == True):
        response = ["POST unsuccessful: snooze already set"]
        response = json.dumps(response)
        return response
    else:
        wake_up_datetime = datetime.datetime.utcnow()+datetime.timedelta(minutes=(5),hours=(-4))
        wake_up_time = str(wake_up_datetime.time())
        with open('globals.json', 'r+') as f:
            data = json.load(f)
            data['snooze_set'] = 1
            data['wake_up_time'] = wake_up_time
            f.seek(0)
            json.dump(data, f, indent=4)
            f.truncate()
        snooze = Alarm()
        snooze.setWakeUpTime(wake_up_time)
        snooze.snooze()

        response = ["POST successful"]
        response = json.dumps(response)
        
        return response

