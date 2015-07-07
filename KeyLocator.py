# This optimized piece of code is possible thanks to:
# pycurl
# RPi.GPIO

import RPi.GPIO as k
import time

import pycurl
from StringIO import StringIO

import json

class KeyLocator:
    
    def __init__(self):

        self.jsonDecoder = json.JSONDecoder()
        k.setmode(k.BCM)
        
        self.pinKey = 18
        self.pinLed = 27
        self.pinAlarm = 4
        
        k.setup(self.pinLed, k.OUT)
        k.setup(self.pinKey, k.IN)
        k.setup(self.pinAlarm, k.IN)
        
        k.output(self.pinLed, 1)
    
    
    def doCurl(self, keyValue = -1, doorValue = -1, messageType = "ping", format = 'json'):
        buffer = StringIO()
        c = pycurl.Curl()
        address = 'http://rneventteknik.se/stage/io/key.php?key='+str(keyValue)+"&door="+str(doorValue)+"&msgType="+str(messageType)+"&format=" + str(format)
        c.setopt(c.URL, address)
        c.setopt(c.WRITEFUNCTION, buffer.write)
        c.perform()
        c.close()
    
        body = buffer.getvalue()
        print body
        
        return self.jsonDecoder.decode(body)
    
    
    def main(self):
        # TODO better name for variable
        pinKeyValue = 0
        done = False
        lastState = 1
        lastTime = time.time()
        sentSMS = False
        response = dict()
        
        while not done:
            # TODO could prabably improve
            pinKeyValue = k.input(self.pinKey)
            pinDoorValue = k.input(self.pinAlarm)
            if not lastState == pinKeyValue:
                k.output(self.pinLed, pinKeyValue)
                response = self.doCurl(keyValue = pinKeyValue, doorValue = pinDoorValue, messageType = "changed")
                lastTime = time.time()
            else:
                currentTime = time.time()
                if currentTime - lastTime > 5.:
                    response = self.doCurl(keyValue = pinKeyValue, doorValue = pinDoorValue, messageType = "ping")
                    
            
            if pinDoorValue and not pinKeyValue and not sentSMS:
                
                
                response = self.doCurl(keyValue = pinKeyValue, doorValue = pinDoorValue, messageType = "key_alarm_alert_emergency")
                self.doSMS(response['feedback'])
                sentSMS = True
            
            if not pinDoorValue and sentSMS:
                sentSMS = False
            
            
            
            lastState = pinKeyValue
            
            time.sleep(1)
            
                
    
            """
            print GPIO.input(button4)
            time.sleep(1)
            if GPIO.input(button4)==1:
                print "fuck yeah"
                GPIO.output(led, 0)
            else:
                GPIO.output(led, 1)
                
            if GPIO.input(button0)==1:
                print "0"
                break
            """
    
    def doSMS(self, smsString):
        
        pycurl_connect = pycurl.Curl()
        pycurl_connect.setopt(pycurl.URL, 'https://api.getsupertext.com/v1/conversations/252585/messages')
        pycurl_connect.setopt(pycurl.HTTPHEADER, ['Auth-Token: 803647742c19c29a3e7bbbc0eddef9ad49ccfbd22c7d304bd929637036b3',
                                                  'application/json, text/javascript, */*; q=0.01'])
        pycurl_connect.setopt(pycurl.POSTFIELDS, "message="+str(smsString)+"&send_to_self=1")
        pycurl_connect.perform()



    
keyLocator = KeyLocator()
keyLocator.main()
    
