# -*- coding: UTF-8 -*-

import serial  # bibliothèque permettant la communication série
import time    # pour le délai d'attente entre les messages
import subprocess #pour lancer des commandes bash
import csv #pour lire le fichier
from threading import Thread #pour le multithread des capteurs de butée
import sys #pour fermer avec sys.exit()
from numpy import sign
import RPi.GPIO as GPIO

#nom des pins des capteurs de butée
butG = 20
butD = 21
butH = 12
butB = 16
bounce = 300

##def des constantes
VmaxX = 90
VmaxY = 300
temps0 = time.time()
temps = 0
ser = serial.Serial('/dev/ttyACM0', 9600)
volume = 0
vitesse = 100
commande = ""
time_omx = ""
msg_ardui = ""
i = 0
tabCommande = [[k/10 for k in range(50)], [k*2 for k in range(50)], [k for k in range(50)]]


##Set up du GPIO
GPIO.setmode(GPIO.BCM)

GPIO.setup(19, GPIO.OUT, initial=GPIO.HIGH)

GPIO.setup(12, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(16, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(20, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(21, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)


def callbackCap(channel):
	if channel == butG :
		ser.write(str.encode("91000"))    #horiz butée gauche
		print("Butée gauche")
	elif channel == butD :
		ser.write(str.encode("90100"))    #horiz butée droite
		print("Butée droite")
	elif channel == butB :
		ser.write(str.encode("90010"))    #verti butée bas
	elif channel == butH :
		ser.write(str.encode("90001"))    #verti butée haut
	else:
		print("Butée detectée sur un pin sans lien avec les capteurs")

GPIO.add_event_detect(butG, GPIO.RISING, callback=callbackCap, bouncetime=bounce)
GPIO.add_event_detect(butH, GPIO.RISING, callback=callbackCap, bouncetime=bounce)
GPIO.add_event_detect(butB, GPIO.RISING, callback=callbackCap, bouncetime=bounce)
GPIO.add_event_detect(butD, GPIO.RISING, callback=callbackCap, bouncetime=bounce)

try:
	while True:
		ser.write(str.encode("S14010E"))
		print("message envoyé")
		time.sleep(0.3)
except KeyboardInterrupt:
    ser.write(str.encode("S00000E"))
    GPIO.cleanup()
    sys.exit()
