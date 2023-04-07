# -*- coding: UTF-8 -*-

##differentes importattions
import time    # pour le délai d'attente entre les messages
import subprocess #pour lancer des commandes bash
import sys #pour fermer avec sys.exit()

import atexit
from gfxhat import touch, lcd, backlight, fonts
from PIL import Image, ImageFont, ImageDraw

##def des constantes



print("""menu-options.py
This example shows how you might store a list of menu options associated
with functions and navigate them on GFX HAT.
Press Ctrl+C or select "Exit" to exit.
""")

width, height = lcd.dimensions()

# A squarer pixel font
#font = ImageFont.truetype(fonts.BitocraFull, 11)

# A slightly rounded, Ubuntu-inspired version of Bitocra
font = ImageFont.truetype(fonts.BitbuntuFull, 10)

image = Image.new('P', (width, height))

draw = ImageDraw.Draw(image)

text = "Bienvenue"

w, h = font.getsize(text)

x = (width - w) // 2
y = (height - h) // 2

class MenuOption:
    def __init__(self, name, action, options=()):
        self.name = name
        self.action = action
        self.options = options
        self.size = font.getsize(name)
        self.width, self.height = self.size

    def trigger(self):
        self.action(*self.options)

def set_backlight(r, g, b):
    backlight.set_all(r, g, b)
    backlight.show()

#menuoption demande le texte, la fonction et les arguments
menu_options = [
            MenuOption('Lancer une musique', set_backlight, (255, 0, 0)),
            MenuOption('Ajouter une musique', set_backlight, (0, 0, 255)),
            MenuOption('Informations', set_backlight, (255, 0, 255)),
            MenuOption('Changer les paramètres', set_backlight, (255, 255, 255)),
            MenuOption('Quitter', sys.exit, (0,))
        ]

current_menu_option = 1

trigger_action = False

def handler(ch, event):
    global current_menu_option, trigger_action
    if event != 'press':
        return
    if ch == 1:
        current_menu_option += 1
    if ch == 0:
        current_menu_option -= 1
    if ch == 4:
        trigger_action = True
    current_menu_option %= len(menu_options)

for x in range(6):
    touch.set_led(x, 0)
    backlight.set_pixel(x, 255, 255, 255)
    touch.on(x, handler)

backlight.show()

def cleanup():
    backlight.set_all(0, 0, 0)
    backlight.show()
    lcd.clear()
    lcd.show()

atexit.register(cleanup)

try:
    draw.text((x, y), text, 1, font)
    for x in range(128):
        for y in range(64):
            pixel = image.getpixel((x, y))
            lcd.set_pixel(x, y, pixel)
    lcd.show()
    time.sleep(3)
    while True:
        image.paste(0, (0, 0, width, height))
        offset_top = 0

        if trigger_action:
            menu_options[current_menu_option].trigger()
            trigger_action = False

        for index in range(len(menu_options)):
            if index == current_menu_option:
                break
            offset_top += 12

        for index in range(len(menu_options)):
            x = 10
            y = (index * 12) + (height / 2) - 4 - offset_top
            option = menu_options[index]
            if index == current_menu_option:
                draw.rectangle(((x-2, y-1), (width, y+10)), 1)
            draw.text((x, y), option.name, 0 if index == current_menu_option else 1, font)

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
