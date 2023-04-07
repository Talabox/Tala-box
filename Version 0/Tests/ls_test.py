import subprocess
import sys
import os

list_of_songs = []
word_number = 0
ls_return = subprocess.check_output(['ls','../Musiques/']).decode()
ls_return = ls_return.splitlines()
for wod in ls_return:
	print(wod[:-4])
os.system('echo "0" > pid.txt')
sys.exit
