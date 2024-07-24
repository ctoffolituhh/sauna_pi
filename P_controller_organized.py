#https://pimylifeup.com/raspberry-pi-temperature-sensor/
#access on 9_3_2023

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


from matplotlib import rcParams

import matplotlib.animation as animation
import numpy as np

next_reading = time.time()

# Setup and configuration
style.use('ggplot')
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BOARD)

# Relay configuration
relay = 8 #board number of the relay pin
GPIO.setup(relay,GPIO.OUT)
GPIO.cleanup()

# PWM configuration
ledpin = 12 # board number of the pwm pin
GPIO.setup(ledpin,GPIO.OUT)
pi_pwm = GPIO.PWM(ledpin,100) #pwm

# DS18B20 configuration
os.system('sudo pigpiod') #dht22
os.system('sudo modprobe w1-gpio') #ds18b20
os.system('sudo modprobe w1-therm') #ds18b20
base_dir = '/sys/bus/w1/devices/' #ds18b20
device_folder = glob.glob(base_dir + '28*')[0] #ds18b20
device_file = device_folder + '/w1_slave' #ds18b20

def read_temp_raw(): #ds18b20
    f = open(device_file, 'r')
    lines = f.readlines()
    f.close()
    return lines

def read_temp(): #ds18b20
    lines = read_temp_raw()
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()
    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos+2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

#plotting code from marius

def read_s1(): #dht22

   r = 0

   next_reading = time.time()
    
   while True: #all dht22, expect where indicated

        r += 1
        s1.trigger()
        time.sleep(0.2)
              local_time = time.ctime()
        print("s1- {}: {:.1f} {:.1f} {:3.2f}".format(
           local_time, s1.humidity(), s1.temperature(), s1.staleness()))    
        print("sp- {}: {:.1f}".format(
           local_time, read_temp()))
  
        #if needed, change the writing file name here
        file = open('sensor_readings_s1.txt', 'a')
        file.write("{}, ".format(local_time))
        file.write("{:.1f}, ".format(s1.humidity()))
        file.write("{:.1f}, ".format(s1.temperature()))
        file.write("{:.2f}\n".format(s1.staleness()))
        file.close()

        #writing a file for the fourth sensor, its name can be changed
        file = open('sensor_readings_sp.txt', 'a')
        file.write("{}, ".format(local_time))
        file.write("{:.1f}\n".format(read_temp()))
        file.close()

        next_reading += INTERVAL
        time.sleep(next_reading-time.time())  # Overall INTERVAL second polling.
      
        return s1.temperature()
    
# PWM control function
refi = []
ref1 = input("Requested temperature: ") 
ref = float(ref1)

def pwmcontrol (ref):

   pi_pwm.start(0)
   ref = ref; #degrees celsius
   P = 10;
   I = 1001;
   #tol = .5;
   eV = 0;
   t = 0;
   t_prev = time.time()
   
   temp = read_temp()
   error = -ref+temp;
   eV = eV+error;
   t_current = time.time()-t_prev;
   t = t_current + t;
   t_prev = time.time();
   ds = error*P+eV*I/t;
   if ds < 0:
        ds = 0;
   if ds >= 100:
        ds = 100;
   print('temperature: '+str(temp))
   print('duty cycle: ' + str(ds))
   print('time: '+str(t))
   #if temp > (ref+tol) and ds <100:
   #    ds = ds + delta_ds
   #if temp < (ref-tol) and ds > 0:
   #    ds = ds - delta_ds
   pi_pwm.ChangeDutyCycle(ds)
  
   time.sleep(4)   

# Plotting and animation function
fig = plt.figure(1)
ax = fig.add_subplot(1, 1, 1)
xs = []    
yp = []    
y1 = []    

def animate(i, xs, yp, y1, refi): 
    my_temp_ps = read_temp()
    my_temp_s1 = read_s1()
    my_time = round(time.time()-start_time,3)
    my_date_string = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
      
    # Add x and y to lists
    xs.append(my_date_string)
    yp.append(my_temp_ps)
    y1.append(my_temp_s1)
    refi.append(ref)

    # Limit x and y lists to 20 items
    #xs = xs[-200:]
    #yp = yp[-200:]
    #yl = y1[-200:]
    #refi = refi[-200:]

    # Draw x and y lists
    ax.clear()
    ax.plot(xs, yp, 'r', label = 'probe sensor')
    ax.plot(xs, y1, 'b', label = 'sensor 1')
    ax.plot(xs, refi, 'g', linestyle = 'dashed', label = 'ref')

    # Format plot
    plt.xticks(rotation=45, ha='right')
    plt.subplots_adjust(bottom=0.30)
    plt.title('Temperature measurement')
    plt.ylabel('Temperature [°C]')
    
    pwmcontrol(ref)
    
start_time = time.time()     #plot
#end of copied code from marius to plot data

if __name__ == "__main__": #dht22

   # Intervals of about 2 seconds or less will eventually hang the DHT22.
   INTERVAL = 5

   pi = pigpio.pi()

   #change the sensor name if needed, change the second argument to the gpio pin used to connect the sensor
   s1 = DHT22.sensor(pi, 2, LED=16, power=8)
    
   ani = animation.FuncAnimation(fig, animate, fargs=(xs, yp, y1, refi), interval=200)    #plot
   plt.show()    #plot
   
s1.cancel()
pi.stop()