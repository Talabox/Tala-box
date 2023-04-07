from time import sleep
import os

os.system('omxplayer -l 00:00:30 musique.wav &')
sleep(3)
os.system('dbuscontrol.sh pause')
sleep(2)
os.system('dbuscontrol.sh pause')
sleep(2)
os.system('pkill -9 omxplayer')

