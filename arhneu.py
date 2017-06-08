#!/usr/bin/env python

# arhn.eu subscription counter for ZEROSEG sample
# Based on the ZEROSEG example libraries
# This is just a poorly written sample for reference only, please keep that in mind.
#
# This script requires the ZeroSeg library
# located at
# https://github.com/AverageManVsPi/ZeroSeg
# 
# The Youtube and Twitch functionality
# uses the official APIs and as such
# require a free dev API keys.
# These need to be filled in the
# respective variables (lines 30 and 59)

import ZeroSeg.led as led
import time
import random
from datetime import datetime
import urllib, json
import RPi.GPIO as GPIO
import threading
switch1 = 17
switch2 = 26
GPIO.setmode(GPIO.BCM)
GPIO.setup(switch1, GPIO.IN)
GPIO.setup(switch2, GPIO.IN) 
#url do liczby subow
url = "https://www.googleapis.com/youtube/v3/channels?part=statistics&forUsername=arhneu&fields=items/statistics/subscriberCount&key=YOUR YOUTUBE API KEY HERE"
ytactive = False
twactive = False
tick = 0;
auto = 0;

def ytsubs():
	global mode
	global tick
	threading.Timer(5.0, ytsubs).start()
	if mode == 1:
		if tick == 0:
			tick = 1
		else:
			tick = 0
		response = urllib.urlopen(url)
		data = json.loads(response.read())
		print "Youtube Refresh: ", data['items'][0]['statistics'].values()[0]
		ytsubs.subs = data['items'][0]['statistics'].values()[0]

def twitch():
	global mode
	global tick
	threading.Timer(5.0, twitch).start()
	if mode == 2:
		if tick == 0:
			tick = 1
		else:
			tick = 0
		response = urllib.urlopen("https://api.twitch.tv/kraken/streams/arhneu?client_id=YOUR TWITCH API KEY HERE")
		data = json.loads(response.read())
		twitch.subs = "OFF";
		if data['stream'] != None:
			print "Twitch Refresh: ", data['stream']['viewers']
			twitch.subs = str(data['stream']['viewers'])
		else:
			print "Twitch Offline"
		
def autogo():
	global mode
	threading.Timer(10.0, autogo).start()
	global auto
	if auto == 1:
		mode += 1
		if mode == 5:
			mode = 1
		print "Auto Switch: ", mode
		
		
device = led.sevensegment(cascaded=2)

#startup
print "Startujemy!"
device.write_text(1, "-ARHNEU-")
#dodaj kropke po N
device.letter(1, 4, "N", 1)
time.sleep(2)
mode = 1;
level = 1;
device.brightness(level)
refresh = 99;
anim = 8;		
		
ytsubs();
twitch();
autogo();

while True:
	now = datetime.now()
	if mode == 1:
		device.write_text(1, "Y " + ytsubs.subs)
		#oznacz odswiezenie kropka
		device.letter(1, 8, "Y", tick)
			
	if mode == 2:
		try:
			getattr(twitch, 'subs')
		except AttributeError:
			device.write_text(1, "T")
			if anim != 8:
				device.letter(1, anim, " ", 1)
			else:
				device.letter(1, anim, "T", 1)
			anim -= 1
			if anim < 1:
				anim = 8
		else:
			device.write_text(1, "T " +	twitch.subs)
			device.letter(1, 8, "T", tick)
	if mode == 3:
		hour = now.hour
		minute = now.minute
		second = now.second
		dot = second % 2 == 0
		# Set hours
		device.letter(1, 8, int(hour / 10))     # Tens
		device.letter(1, 7, hour % 10)     # Ones
		device.letter(1, 6, " ", 1)
		# Set minutes
		device.letter(1, 5, int(minute / 10))   # Tens
		device.letter(1, 4, minute % 10)        # Ones
		device.letter(1, 3, " ", 1)
		# Set seconds
		device.letter(1, 2, int(second / 10))   # Tens
		device.letter(1, 1, second % 10)        # Ones
	if mode == 4:
		day = now.day
		month = now.month
		year = now.year - 2000

		# Set day
		device.letter(1, 8, int(day / 10))     # Tens
		device.letter(1, 7, day % 10)          # Ones
		device.letter(1, 6, '-')               # dash
		# Set day
		device.letter(1, 5, int(month / 10))     # Tens
		device.letter(1, 4, month % 10)     # Ones
		device.letter(1, 3, '-')               # dash
		# Set day
		device.letter(1, 2, int(year / 10))     # Tens
		device.letter(1, 1, year % 10)     # Ones
	if mode == 5:
		auto = 1;	
		mode = 1;
	
	if not GPIO.input(switch2):
		if auto == 1:
			auto = 0
			mode = 1
			print "Auto Off"
		elif mode < 6:
			mode += 1
		else:
			mode = 1
		if mode == 1:
			device.write_text(1, "SUBY YT")
		if mode == 2:
			device.write_text(1, "LIVE")
		if mode == 3:
			device.write_text(1, "CZAS")
		if mode == 4:
			device.write_text(1, "DATA")
		if mode == 5:
			device.write_text(1, "AUTO")
		time.sleep(1)
	#wskaznik jasnosci
	elif not GPIO.input(switch1):
		if level <= 2:
			level = 5
		elif level == 5:
			level = 10
		elif level == 10:
			level = 14
		elif level >= 14:
			level = 1
		device.brightness(level)
		print "Poziom jasnosci:", level
		time.sleep(0.5);
	else:
		pass