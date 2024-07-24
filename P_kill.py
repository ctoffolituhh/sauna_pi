#code from:
#https://pimylifeup.com/raspberry-pi-temperature-sensor/
#copied on 9_3_2023

import os
import glob
import time
import atexit
import pigpio
import DHT22 #header file with classes etc
import RPi.GPIO as GPIO

import datetime

import matplotlib
matplotlib.use('TkAgg')

import matplotlib.pyplot as plt
import matplotlib.lines as Line2D

from matplotlib import style
style.use('ggplot')

from matplotlib import rcParams

import matplotlib.animation as animation
import numpy as np


next_reading = time.time()

ledpin = 12

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BOARD)
GPIO.setup(ledpin,GPIO.OUT)

pi_pwm = GPIO.PWM(ledpin,100) #pwm


os.system('sudo pigpiod') #dht22

os.system('sudo modprobe w1-gpio') #ds18b20
os.system('sudo modprobe w1-therm') #ds18b20

base_dir = '/sys/bus/w1/devices/' #ds18b20
device_folder = glob.glob(base_dir + '28*')[0] #ds18b20
device_file = device_folder + '/w1_slave' #ds18b20

if __name__ == "__main__": #dht22

   # Intervals of about 2 seconds or less will eventually hang the DHT22.
   INTERVAL = 5

   pi = pigpio.pi()

   #change the sensor name if needed, change the second argument to the gpio pin used to connect the sensor
   s1 = DHT22.sensor(pi, 2, LED=16, power=8)
   
pi_pwm.stop()

s1.cancel()

GPIO.cleanup()

GPIO.setmode(GPIO.BOARD)
GPIO.setup(8, GPIO.OUT)
GPIO.output(8, GPIO.LOW)
 
pi.stop()