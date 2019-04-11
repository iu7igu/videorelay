#!/usr/bin/env python3

import os
import time
import configparser
from sys import platform
import datetime

config = configparser.ConfigParser()
config.read("videorelay.conf")

pin = int(config.get("VideoRelay", "GPIO"))
percorso = str(config.get("VideoRelay","Percorso"))
canale = str(config.get("VideoRelay", "Canalevideo"))
delay = int(config.get("VideoRelay", "Delay"))
pesominimo = int(config.get("VideoRelay", "PesoMinimo"))
percorsolog = str(config.get("VideoRelay", "PercorsoLog"))
abilitalog = int(config.get("VideoRelay", "AbilitaLog"))

if abilitalog:
    log=open(percorsolog, "w")
	
def preleva():
    os.system("ffmpeg -y -f video4linux2 -i /dev/video"+canale+" -vframes 1 "+ percorso + "> /dev/null")
    if abilitalog:
        log.write(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S') + "-----> scattata immagine - peso: "+ str(os.path.getsize(percorso))+"\n")
        
if platform == "linux" or platform == "linux2":
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.OUT)
    vox = True
    GPIO.output(pin, GPIO.LOW)        
    try:
        while 1:
            if vox:
                preleva()
                if int(os.path.getsize(percorso)) >= pesominimo:
                    GPIO.output(pin, GPIO.HIGH)
                    if abilitalog:
                        log.write(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S') + "-----> Attivo rele\n")
                    tempo = time.time()
                    vox = False
            if vox == False:
                if time.time() >= tempo+delay:
                    preleva()
                    if int(os.path.getsize(percorso)) <= pesominimo:
                        vox = True
                        GPIO.output(pin, GPIO.LOW)
                        if abilitalog:
                            log.write(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S') + "-----> Disattivo rele\n")
                    else :
                        vox = False
                time.sleep(1)
    except KeyboardInterrupt: # If CTRL+C is pressed, exit cleanly:
        if abilitalog:
            log.write(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S') + "-----> CTRL + C\n")
    finally:
        if abilitalog:
            log.write(datetime.datetime.now().strftime('%d-%m-%Y %H:%M:%S') + "-----> Chiudo e resetto i GPIO\n")
            log.close()
        GPIO.cleanup() # cleanup all GPIO 
