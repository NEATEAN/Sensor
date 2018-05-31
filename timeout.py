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

conn=pymysql.connect(host="220.149.235.54", user="dku18", passwd="1234", db="yedam")

def read_spi(adcchannel):
  if adcchannel >7 or adcchannel<0:
    return -1
  buff=spi.xfer2([1,(8+adcchannel)<<4,0])
  adcValue=((buff[1]&3)<<8)+buff[2]
  return adcValue

def average(values):
  if len(values)==0: 
   return None
#  x=[]
  return sum(values, 0.0) /len(values)


try : 
  with conn.cursor() as cur : 
    sql="insert into gain(date_pre, date_suf, date, CO, Temperature, Humidity, Place) values(%s, %s, %s, %s, %s, %s, %s)"
    
    while True:
      array_co=[] #CO
      array_te=[] #tem 
      array_hu=[] #hu

      time1=int(time.strftime('%M', time.localtime()))

      while True: 

        time2=int(time.strftime('%M', time.localtime()))

        if (time2-time1>=10 ) or (time2-time1<=-10):
          break;
          
        humidity, temperature = Adafruit_DHT.read_retry(sensor, pin)
        adcvalue=read_spi(adcchannel)

        if humidity is not None and temperature is not None:
        
          array_co.append(adcvalue)
          array_te.append(temperature)
          array_hu.append(humidity)
        else :
          
          print("Failed to get reading.")
          exit()

 #       print(array_te)
 #       print(array_hu)
 #       print(array_co)
 
        time.sleep(10)

      temperature=average(array_te)
      humidity=average(array_hu)
      adcvalue=max(array_co)

      print('Temp={0:0.1f}*C  Humidity={1:0.1f}%'.format(temperature, humidity)) 
      print('CO = %d'%(adcvalue))
      print(time.strftime('%Y%m%d', time.localtime()),time.strftime('%H%M%S', time.localtime()), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),adcvalue,temperature, humidity, space)
         
      try : 

        cur.execute(sql,(time.strftime('%Y%m%d', time.localtime()),time.strftime('%H%M%S', time.localtime()), time.strftime('%Y-%m-%d %H:%M:%S', time.localtime()),adcvalue,temperature, humidity, space))
        conn.commit()

      except TimeoutError as e:
        print("timeoutError")
        continue

except TimeoutError as e:
  print("Cannot connect DB")
  exit()        
except KeyboardInterrupt:
  exit()
finally:
  conn.close()
