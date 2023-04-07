# -*- coding: UTF-8 -*-

##differentes importattions
import serial  # Serial communication
import time    # Delay between messages
import subprocess #To launch bash commands
import csv #To read .csv file
import sys #To close using sys.exit()
import os
from numpy import sign
import RPi.GPIO as GPIO #For the pins and the threading
GPIO.setmode(GPIO.BCM)  
GPIO.setwarnings(False) #To silence conflicts on pins assumed to be taken

##Write Pid in txt file to kill this script
pid = str(os.getpid())
pid_file = open("/home/pi/Documents/Talabox/pid.txt","w")
pid_file.write(pid)
pid_file.close()


args = sys.argv
music_name = args[1]
#En pas par secondes, doit correspondre à la valeure donnée dans le script de l'arduino
Vmax = 4800

Lx = 5300
Ly = 2000 #TODO

current_time = 0
ser = serial.Serial('/dev/ttyACM0', 9600)
ser.flushInput()
volume = 0
speed_coef = 100
commande = ""
time_omx = ""
msg_ardui = ""
i = 0
command_list = []
switch_left = 12
switch_right = 16
switch_top = 20
switch_bottom = 21
switch_left2 =18 
switch_right2 =23
switch_top2 =24
switch_bottom2 =25
bounce = 100

##Set up du GPIO

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

GPIO.setup(13, GPIO.OUT, initial=GPIO.HIGH)

GPIO.setup(switch_left, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(switch_right, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(switch_top, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(switch_bottom, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(switch_left2, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(switch_right2, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(switch_top2, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)
GPIO.setup(switch_bottom2, GPIO.IN,pull_up_down=GPIO.PUD_DOWN)


#During initialisation the first row of command_list will change 
#according to the activation of the limit switches
def callbackCap(channel):
    #First movable arm
    if channel == switch_left :
        print("G")
        ser.write(str.encode("S9100090000E"))    #horiz left
        command_list[0][1]=100

    elif channel == switch_right :
        print("D")
        ser.write(str.encode("S9010090000E"))    #horiz right
        command_list[0][1]=0

    elif channel == switch_bottom :
        print("B")
        ser.write(str.encode("S9001090000E"))    #verti down
        command_list[0][2]=0
        
    elif channel == switch_top :
        print("H")
        ser.write(str.encode("S9000190000E"))   #verti up
        command_list[0][2]=100
        
    #Second movable arm 
    elif channel == switch_left2 :
        print("G2")
        ser.write(str.encode("S9000091000E"))    #horiz left
        command_list[0][3]=100

        
    elif channel == switch_right2 :
        print("D2")
        ser.write(str.encode("S9000090100E"))    #horiz right
        command_list[0][3]=0

    elif channel == switch_bottom2 :
        print("B2")
        ser.write(str.encode("S9000090010E"))    #verti down
        command_list[0][4]=0

    elif channel == switch_top2 :
        print("H2")
        ser.write(str.encode("S9000090001E"))   #verti up
        command_list[0][4]=100



GPIO.add_event_detect(switch_left, GPIO.RISING, callback=callbackCap, bouncetime=bounce)
GPIO.add_event_detect(switch_top, GPIO.RISING, callback=callbackCap, bouncetime=bounce)
GPIO.add_event_detect(switch_bottom, GPIO.RISING, callback=callbackCap, bouncetime=bounce)
GPIO.add_event_detect(switch_right, GPIO.RISING, callback=callbackCap, bouncetime=bounce)
GPIO.add_event_detect(switch_left2, GPIO.RISING, callback=callbackCap, bouncetime=bounce)
GPIO.add_event_detect(switch_top2, GPIO.RISING, callback=callbackCap, bouncetime=bounce)
GPIO.add_event_detect(switch_bottom2, GPIO.RISING, callback=callbackCap, bouncetime=bounce)
GPIO.add_event_detect(switch_right2, GPIO.RISING, callback=callbackCap, bouncetime=bounce)

# ##
# 
# #TODO fonction qui calcule la distance parcourue pour de vrai si jamais le chariot est trop lent afin de changer la case suivant
# 

#Transform int to string
def int_to_str(a):
    if a<10:
        return str("0"+str(a)[0:1])
    else:
        return str(a)[0:2]

#Create table that contains all the movement commands (from the .csv file)
def get_list():
    newTab = [[-0.1,1,1,1,1]]
    with open('/home/pi/Documents/Commandes/' + music_name + '.csv', 'r') as file:
        reader = csv.reader(file, delimiter=";")
        for row in reader:
            new_row = [float(row[0]), float(row[1]), float(row[2]),float(row[3]), float(row[4])]
            newTab+=[new_row]
    file.close()
    return newTab

#Transfom position command to speed command
#passage d'une consigne de position en consigne de vitesse, en vérifiant les limites du moteur
#numb permet d'indiquer le rail, 0 pour le 1er, 2 pour le 2eme
def dist_to_speed(dx,dy,ts,numb):
    global command_list, i
    dx = dx*Lx/(Vmax*ts)
    dy = dy*Ly/(Vmax*ts)
    if dx > 99:
        command_list[i][1+numb] = command_list[i-1][1+numb] + (99/dx)*(command_list[i][1+numb]-command_list[i-1][1+numb])
    if dy > 99:
        command_list[i][2+numb] = command_list[i-1][2+numb] + (99/dy)*(command_list[i][2+numb]-command_list[i-1][2+numb])
    return min(dx,99),min(dy,99)

#Create arduino message from de command_list positions
#The actual row and the previous row of command_list are compared and the 
#movement is chosen depending on the relative position of the movable arms
def asserv(tabNx , tabPv):
    t = tabNx[0]-tabPv[0]
    l = tabNx[1]-tabPv[1]
    h = tabNx[2]-tabPv[2]
    l2 = tabNx[3]-tabPv[3]
    h2 = tabNx[4]-tabPv[4]
    if l>0:
        if h>0: sens = 2 #right, up
        else : sens = 3 #right, down
    else:
        if h>0: sens = 0 #left, up
        else : sens = 1 #left, down
    if l2>0:
        if h2>0: sens2 = 2 #right, up
        else : sens2 = 3 #right, down
    else:
        if h2>0: sens2 = 0 #left, up
        else : sens2 = 1 #left, down
    l,h = dist_to_speed(abs(l),abs(h),t,0)
    l2,h2 = dist_to_speed(abs(l2),abs(h2),t,2)
    #First number: direction arm 1
    #Second, third number: speed arm 1
    #Fourth, fifth number: 
    
    commande = str(sens)+int_to_str(l)+int_to_str(h)+str(sens2)+int_to_str(l2)+int_to_str(h2)
    return commande

#Initialise the position to the left and down for the first arm (x=0;y=0)
def initPosition():
    global command_list
    while (command_list[0][3]==1 or command_list[0][4] == 1):
        #Movement X and Y of the first arm
        if (command_list[0][3]==1 and command_list[0][4]==1):
            #If message starts by 1, the limit switches have not been activated yet, so the motors start work
            #During the initialisation the arm moves until the correct limit switch
            #Message in arduino: S1.........E   
            #Speed X=25
            #Speed Y=10
            
            ser.write(str.encode("S1251010000E"))
        #Movement Y of the first arm
        if command_list[0][3]==0 :
            ser.write(str.encode("S1001010000E"))
        #Movement X of the first arm 
        if command_list[0][4]==0 :
            ser.write(str.encode("S1250010000E"))
        time.sleep(0.1)
    #Stop the motors    
    ser.write(str.encode("S0000000000E"))
    

#Initialise the position to the left and down for the second arm (x=0;y=0)
def initPosition2():
    global command_list
    while (command_list[0][1]==1 or command_list[0][2] == 1):
        #Movement X and Y of the second arm
        if (command_list[0][1]==1 and command_list[0][2]==1):
            ser.write(str.encode("S1000012510E"))
        #Movement Y of the second arm
        if command_list[0][1]==0 :
            ser.write(str.encode("S1000010010E"))
        #Movement X the second arm
        if command_list[0][2]==0 :
            ser.write(str.encode("S1000012500E"))

        time.sleep(0.1)
    ser.write(str.encode("S0000000000E"))

#Convert volume into a command according to omxplayer format
def music_volume(valCommande):
    return (int(valCommande)-50)*19


#All the functions above
try:
    command_list = get_list()
    initPosition()
    initPosition2()
    
    print("Start")
    current_time = time.time()
    subprocess.Popen(["omxplayer",'/home/pi/Documents/Musiques/' + music_name + '.wav'])
    #TODO time.sleep(0.3)
    for i in range(1,len(command_list)):
        #Check the file "commande.txt"
        commande = subprocess.check_output(['tail','-1','/home/pi/Documents/Talabox/commande.txt']).decode()
        #If the command is 0, we stop the motors
        if int(commande[0])==0:
            ser.write(str.encode("S0000000000E"))
            subprocess.Popen(["dbuscontrol.sh","pause"])
            while int(commande[0])==0:
                time.sleep(0.1)
                commande = subprocess.check_output(['tail','-1','/home/pi/Documents/Talabox/commande.txt']).decode()
            subprocess.Popen(["dbuscontrol.sh","pause"])
            current_time = time.time()
        #If the command is 1, we play the music and start the movement
        elif int(commande[0])==1:
            vitesse = int(commande[2:4])
            if int(volume)!=music_volume(commande[6:9]):
                volume = str(music_volume(commande[6:9]))
                subprocess.Popen(["pkill","omxplayer"])
                tps = command_list[i][0]
                time_omx = str(int(tps/3600))+ ":" + str(int((tps%3600)/60)) + ":" + str(int(tps%60))
                subprocess.Popen(["omxplayer","--vol",volume,"-l",time_omx,'/home/pi/Documents/Musiques/' + music_name + '.wav'])
            #Create message that will be passed through the arduino serial
            msg_ardui = asserv(command_list[i],command_list[i-1])
            #Write the message at the serial
            ser.write(str.encode("S"+msg_ardui+"E"))
            current_time = current_time+(command_list[i][0]-command_list[i-1][0])
            time.sleep(max(current_time-time.time(),0))
        else:
            #If the command is a different number than 0 or 1 there's an error so we stop the program
            subprocess.Popen(["pkill","omxplayer"])
            ser.write(str.encode("S0000000000E"))
            pid_file = open("pid.txt","w")
            pid_file.write("0")
            pid_file.close()
            sys.exit()

#If we press ctrl+c we exit the program properly
except KeyboardInterrupt: 
    subprocess.Popen(["pkill","omxplayer"])
    ser.write(str.encode("S0000000000E"))
    pid_file = open("/home/pi/Documents/Talabox/pid.txt","w")
    pid_file.write("0")
    pid_file.close()
    sys.exit()


subprocess.Popen(["pkill","omxplayer"])
ser.write(str.encode("S0000000000E"))
pid_file = open("/home/pi/Documents/Talabox/pid.txt","w")
pid_file.write("0")
pid_file.close()
sys.exit()
