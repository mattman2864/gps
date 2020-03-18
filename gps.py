import socket
import time
import pynmea2
import math
from tkinter import *
from geopy.distance import great_circle
import numpy as np

def calculate_initial_compass_bearing(pointA, pointB): #DIRECTION BETWEEN TWO POINTS
    if (type(pointA) != tuple) or (type(pointB) != tuple):
        raise TypeError("Only tuples are supported as arguments")
    lat1 = math.radians(pointA[0])
    lat2 = math.radians(pointB[0])
    diffLong = math.radians(pointB[1] - pointA[1])
    x = math.sin(diffLong) * math.cos(lat2)
    y = math.cos(lat1) * math.sin(lat2) - (math.sin(lat1) * math.cos(lat2) * math.cos(diffLong))
    initial_bearing = math.atan2(x, y)
    initial_bearing = math.degrees(initial_bearing)
    compass_bearing = (initial_bearing + 360) % 360
    return compass_bearing

def nmea2d(n,a):
    if n[4] == '.':
        D=n[:2]
        M=n[2:]
        M=float(M)/60
        if a == 'S':
            return -(float(D)+M)
        else:
            return float(D)+M
    else:
        D=n[:3]
        M=n[3:]
        M=float(M)/60
        if a == 'W':
            return -(float(D)+M)
        else:
            return float(D)+M
    
def geocache():
    try:  
        lat = float(input('enter the latitude of your geocache: '))
        lon = float(input('enter the longitude of your geocache: '))
    except ValueError:
        print('invalid coordinates')
        return 'invalid','invalid'
    return lat,lon

def pol2cart(rho, phi,oX,oY):
    x = rho * np.cos(phi) + oX
    y = rho * np.sin(phi) + oY
    return(x, y)

cachelat,cachelon = geocache()
while cachelat == 'invalid' or cachelon == 'invalid':
    geocache()
    if cachelat != 'invalid' and cachelon != 'invalid':
        break    
UDP_IP = socket.gethostbyname(socket.gethostname())
UDP_PORT = 11123
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP
sock.bind((UDP_IP, UDP_PORT))
root = Tk()
cnv = Canvas(root, width=500, height=500)
cnv.pack()
with open('gps_rx.data','a') as f:
    try:
        while True:
          data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
          now = time.time()
          datastr = "%d %s"%(now,data)
          msg = pynmea2.parse(data.decode('utf-8'))
          latitude = nmea2d(msg.lat,msg.lat_dir)
          longitude = nmea2d(msg.lon,msg.lon_dir)
          print('data recieved: \n',data,'\n')
          distance = float(str(great_circle((latitude,longitude),(cachelat,cachelon)))[:13])
          direction = (calculate_initial_compass_bearing((float(latitude),float(longitude)),(cachelat,cachelon)))
          coords = msg.lat,', ',msg.lon
          
          if direction < 22.5 or direction > 337.5:
              cardinal = 'N'
          elif direction < 67.5:
              cardinal = 'NE'
          elif direction < 112.5:
              cardinal = 'E'
          elif direction < 157.5:
              cardinal = 'SE'
          elif direction < 202.5:
              cardinal = 'S'
          elif direction < 247.5:
              cardinal = 'SW'
          elif direction < 292.5:
              cardinal = 'W'
          elif direction < 337.5:
              cardinal = 'NW'
          
          cnv.delete('all')
          cnv.create_rectangle(0,0,500,500,fill='white')
          cnv.create_oval(pol2cart(200,direction,245,245)[0], pol2cart(200,direction,245,245)[1], pol2cart(200,direction,255,255)[0], pol2cart(200,direction,255,255)[1],fill='red')
          cnv.create_oval(pol2cart(200,180+direction,245,245)[0], pol2cart(200,180+direction,245,245)[1], pol2cart(200,180+direction,255,255)[0], pol2cart(200,180+direction,255,255)[1],fill='blue')
          cnv.create_line(pol2cart(200,180+direction,250,250)[0], pol2cart(200,180+direction,250,250)[1],pol2cart(200,direction,250,250)[0], pol2cart(200,direction,250,250)[1])
          cnv.create_line(50,450,450,450)
          cnv.create_line(50,425,50,475)
          cnv.create_line(450,425,450,475)
          scale = round(distance),' km'
          cnv.create_text(200,440,text=scale)
          cnv.create_text(100,325,text='distance: %s' % distance)
          cnv.create_text(100,340,text='direction: %s' % cardinal)
          cnv.create_text(100,355,text='latitude: %s' % latitude)
          cnv.create_text(100,370,text='Longitude: %s' % longitude)
          cnv.update()
          
          f.write(datastr)
          f.flush()
    finally:
        sock.close()
        cnv.destroy()
