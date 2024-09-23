import os
import time

print("Turning off room...")

#runs command to turn on speaker
os.system('irsend SEND_ONCE EDIFIER KEY_POWER')
time.sleep(1)

#runs command to turn on tv
os.system('irsend SEND_ONCE SAMSUNG_AA59-00600A_POWER KEY_POWER')
time.sleep(1)

# runs command to wake computer
os.system('net rpc shutdown -I ip.address -U "USER"%"PASSWORD"')
