# -*- coding: UTF-8 -*-

##differentes importattions
import time    # pour le délai d'attente entre les messages
import subprocess #pour lancer des commandes bash
import sys #pour fermer avec sys.exit()
import os
import signal

import atexit
from gfxhat import touch, lcd, backlight, fonts
from PIL import Image, ImageFont, ImageDraw

##Initialization of variables and font definition

print("""Press Ctrl+C or select "Exit" to exit.""")

mounted = 1

width, height = lcd.dimensions()
current_menu = 0

font = ImageFont.truetype(fonts.BitbuntuFull, 10)

image = Image.new('P', (width, height))

draw = ImageDraw.Draw(image)

text = "Bienvenue"

w, h = font.getsize(text)

x = (width - w) // 2
y = (height - h) // 2

##Definition of the Menu's options and the fonctions to navigate it
class MenuOption:
    def __init__(self, name, action, options=()):
        self.name = name
        self.action = action
        self.options = options
        self.size = font.getsize(name)
        self.width, self.height = self.size

    def trigger(self):
        self.action(*self.options)

def set_menu(menu_number):
    global current_menu,current_menu_option, menu_options
    current_menu_option = 0
    current_menu = menu_number
    if current_menu == 1:
        commande = subprocess.check_output(['tail','-1','/home/pi/Documents/Talabox/commande.txt']).decode()
        commande = commande.split(" ")
        commande[0]= "1"
        commande = commande[0]+" "+commande[1]+" "+commande[2]
        commande_file = open("/home/pi/Documents/Talabox/commande.txt","w")
        commande_file.write(commande)
        commande_file.close()
        subprocess.Popen(["python3","/home/pi/Documents/Talabox/deplacement.py",subprocess.check_output(['tail','-1','/home/pi/Documents/Talabox/current_song_name.txt']).decode()])
    elif current_menu == 2:
        menu_options[2] = []
        ls_return = subprocess.check_output(['ls','/home/pi/Documents/Commandes/']).decode()
        list_of_songs = ls_return.splitlines()
        for song in list_of_songs:
            menu_options[2].append(MenuOption(song, set_to_song , (song[:-4],)))
        menu_options[2].append(MenuOption("Retour", set_menu , (0,)))

    elif current_menu == 3:
        global mounted
        menu_options[3] = []
        if mounted == 1 :
            subprocess.run(["sudo","mount","/dev/sda1", "/mnt/usbStick/"])
            mounted = subprocess.call("mount | grep /mnt/usbStick", shell=True)
        if mounted == 0:
            ls_return = subprocess.check_output(['ls','/mnt/usbStick/Talasound/']).decode()
            list_of_songs = ls_return.splitlines()
        else :
            list_of_songs = []
            menu_options[3].append(MenuOption("Usb non detectee", set_menu , (0,)))
        for song in list_of_songs:
            menu_options[3].append(MenuOption(song, get_song , (song[:-4],)))
        menu_options[3].append(MenuOption("Retour", set_menu , (0,)))


def get_song(song_name):
    file_path = "/mnt/usbStick/Talasound/"+song_name+".wav"
    subprocess.call(["sudo","cp",file_path,"/home/pi/Documents/Musiques/"])

    width, height = lcd.dimensions()
    font = ImageFont.truetype(fonts.BitbuntuFull, 10)
    image = Image.new('P', (width, height))
    draw = ImageDraw.Draw(image)
    text = "Chargement..."
    w, h = font.getsize(text)
    x = (width - w) // 2
    y = (height - h) // 2
    draw.text((x, y), text, 1, font)
    for x in range(128):
        for y in range(64):
            pixel = image.getpixel((x, y))
            lcd.set_pixel(x, y, pixel)
    lcd.show()

    subprocess.call(["python3","/home/pi/Documents/Talabox/AnalyseSon.py",song_name])
    subprocess.run(["sudo",'chmod','755','/home/pi/Documents/Commandes/'+song_name+".csv"])
    set_to_song(song_name)

def set_to_song(song_name):
    global current_menu,current_menu_option
    current_menu = 0
    current_menu_option = 0
    song_name_file = open("/home/pi/Documents/Talabox/current_song_name.txt","w")
    song_name_file.write(song_name)
    song_name_file.close()

def stop(menu_number):
    global current_menu,current_menu_option
    current_menu = 0
    current_menu_option = 0
    pid = int(subprocess.check_output(['tail','-1','/home/pi/Documents/Talabox/pid.txt']).decode())
    if pid != 0 :
        os.kill(pid,signal.SIGINT)
        os.system('echo "0" > /home/pi/Documents/Talabox/pid.txt')

def pause(menu_number):
    global current_menu,current_menu_option
    current_menu_option = 0
    current_menu = menu_number
    if current_menu == 4:
        commande = subprocess.check_output(['tail','-1','/home/pi/Documents/Talabox/commande.txt']).decode()
        commande = commande.split(" ")
        commande[0]= "0"
        commande = commande[0]+" "+commande[1]+" "+commande[2]
        commande_file = open("/home/pi/Documents/Talabox/commande.txt","w")
        commande_file.write(commande)
        commande_file.close()
    elif current_menu == 1:
        commande = subprocess.check_output(['tail','-1','/home/pi/Documents/Talabox/commande.txt']).decode()
        commande = commande.split(" ")
        commande[0]= "1"
        commande = commande[0]+" "+commande[1]+" "+commande[2]
        commande_file = open("/home/pi/Documents/Talabox/commande.txt","w")
        commande_file.write(commande)
        commande_file.close()

## Creation of the menu in use
menu_options = [[
            MenuOption('Jouer la musique', set_menu, (1,)),
            MenuOption('Choisir une musique', set_menu, (2,)),
            MenuOption('Ajouter une musique', set_menu, (3,)),
            MenuOption('Informations',set_menu,(5,)),
            MenuOption('Quitter', sys.exit, (0,))
            ] ,
            [
            MenuOption('Mettre en pause', pause,(4,)),
            MenuOption('Arreter',stop,(0,))
            ],
            [],
            [],
            [
            MenuOption('Reprendre', pause,(1,)),
            MenuOption('Arreter',stop,(0,))
            ],
            [
            MenuOption('Pour quitter:',set_menu, (0,)),
            MenuOption('appuyez sur valider',set_menu, (0,)),
            MenuOption('',set_menu, (0,)),
            MenuOption('Si Choisir est' ,set_menu,(0,)),
            MenuOption('vide pensez à faire',set_menu, (0,)),
            MenuOption('Ajouter avant',set_menu, (0,)),
            MenuOption('',set_menu, (0,)),
            MenuOption('Si Ajouter est vide',set_menu, (0,)),
            MenuOption('Créez un dossier:',set_menu, (0,)),
            MenuOption('Talasound',set_menu, (0,)),
            MenuOption("sur la base de l'usb",set_menu, (0,)),
            MenuOption('la musique doit être',set_menu, (0,)),
            MenuOption('au format .wav',set_menu, (0,)),
            MenuOption('Des convertisseurs',set_menu, (0,)),
            MenuOption('existent en ligne',set_menu, (0,)),
            MenuOption('',set_menu, (0,))
            ]
        ]

current_menu_option = 1

trigger_action = False

##
def handler(ch, event):
    global current_menu_option, trigger_action,current_menu
    if event != 'press':
        return
    if ch == 1:
        current_menu_option += 1
    if ch == 0:
        current_menu_option -= 1
    if ch == 4:
        trigger_action = True
    current_menu_option %= len(menu_options[current_menu])

for x in range(6):
    touch.set_led(x, 0)
    backlight.set_pixel(x, 255, 255, 255)
    touch.on(x, handler)

backlight.show()

def cleanup():
    global mounted
    backlight.set_all(0, 0, 0)
    backlight.show()
    lcd.clear()
    lcd.show()
    pid = int(subprocess.check_output(['tail','-1','/home/pi/Documents/Talabox/pid.txt']).decode())
    if pid != 0 :
        os.kill(pid,signal.SIGINT)
        os.system('echo "0" > /home/pi/Documents/Talabox/pid.txt')
    if mounted == 0:
        subprocess.run(["sudo","umount","/mnt/usbStick/"])

atexit.register(cleanup)

def gestionMenu(menu_opt):
    global trigger_action, current_menu_option, offset_top
    if trigger_action:
        menu_opt[current_menu_option].trigger()
        trigger_action = False

    for index in range(len(menu_opt)):
        if index == current_menu_option:
            break
        offset_top += 12

    for index in range(len(menu_opt)):
        x = 10
        y = (index * 12) + (height / 2) - 4 - offset_top
        option = menu_opt[index]
        if index == current_menu_option:
            draw.rectangle(((x-2, y-1), (width, y+10)), 1)
        draw.text((x, y), option.name, 0 if index == current_menu_option else 1, font)

##Main loop
try:
    #Print "Bienvenue" for 3 sec
    draw.text((x, y), text, 1, font)
    for x in range(128):
        for y in range(64):
            pixel = image.getpixel((x, y))
            lcd.set_pixel(x, y, pixel)
    lcd.show()
    time.sleep(3)

    #Print Menu and wait for input
    while True:
        image.paste(0, (0, 0, width, height))
        offset_top = 0

        gestionMenu(menu_options[current_menu])

        w, h = font.getsize('>')
        draw.text((0, (height - h) / 2), '>', 1, font)

        for x in range(width):
            for y in range(height):
                pixel = image.getpixel((x, y))
                lcd.set_pixel(x, y, pixel)

        lcd.show()
        time.sleep(1.0 / 30)

except KeyboardInterrupt:
    cleanup()
    sys.exit()
