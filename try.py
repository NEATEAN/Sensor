#!/usr/bin/python
# This Python file uses the following encoding:utf-8
import RPi.GPIO as GPIO
import sys
import time
import Adafruit_DHT
import spidev
import pymysql

sensor = Adafruit_DHT.DHT11

pin=2
adcchannel=0
space=1

spi=spidev.SpiDev()
spi.open(0,0)

RETRIES = 3
TIMEOUT = 10
def read_spi(adcchannel):
  if adcchannel >7 or adcchannel<0:
    return -1
  buff=spi.xfer2([1,(8+adcchannel)<<4,0])
  adcValue=((buff[1]&3)<<8)+buff[2]
  return adcValue

def average(values):
  if len(values)==0: 
   return None
  x=[]
  return sum(values, 0.0) /len(values)

while True: 
  try : 
    conn=pymysql.connect(host="220.149.235.54", user="dku18", passwd="1234", db="yedam")
    with conn.cursor() as cur : 
      sql="insert into gain(date_pre, date_suf, date, CO, Temperature, Humidity, Place) values(%s, %s, %s, %s, %s, %s, %s)"
      
      while True:
        x=[] #CO
        y=[] #tem 
        z=[] #hu

        time1=int(time.strftime('%M', time.localtime()))
 
        while True: 

          time2=int(time.strftime('%M', time.localtime()))

          if (time2-time1>=10 ) or (time2-time1<=-10):
            break;
          
          humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
          adcvalue=read_spi(adcchannel)
        
          x.append(adcvalue)
          y.append(temperature)
          z.append(humidity)
 #       print(x)
 
          time.sleep(10)

        temperature=average(y)
        humidity=average(z)
        adcvalue=max(x)

        if humidity is not None and temperature is not None:
          print(time.strftime('%Y%m%d', time.localtime()),time.strftime('%H%M%S', time.localtime()), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),adcvalue,temperature, humidity, space)
          
          try :  
            cur.execute(sql,(time.strftime('%Y%m%d', time.localtime()),time.strftime('%H%M%S', time.localtime()), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),adcvalue,temperature, humidity, space))
            conn.commit()
          except:
            conn.rollback()
            print("DB Error : Cannot Execute Query")
        else :
          print("Failed to get reading.")
        
  except TimeoutError:
    print("Time out")
    continue         
  except KeyboardInterrupt:
    exit()
  finally:
    conn.close()
