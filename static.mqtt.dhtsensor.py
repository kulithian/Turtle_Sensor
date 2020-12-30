#!/usr/bin/python
# DHT Sensor Data-logging to MQTT Temperature channel

import json
import requests
import sys
import time
import datetime
import paho.mqtt.client as mqtt
import Adafruit_DHT


#==================================================================================================================================================
#Usage
#python mqtt.channel.py <temp topic> <humidity topic> <gpio pin> <optional update frequency>
# eg python mqtt.channel.py 'cupboard/temperature1' 'cupboard/humidity1' 4
# will start an instance using 'cupboard/temperature1' as the temperature topic, and using gpio port 4 to talk to a DHT22 sensor
# it will use the default update time of 300 secons.
#==================================================================================================================================================

# Type of sensor, can be Adafruit_DHT.DHT11, Adafruit_DHT.DHT22, or Adafruit_DHT.AM2302.
DHT_TYPE = Adafruit_DHT.DHT22

# Example of sensor connected to Raspberry Pi pin 23
DHT_PIN  = 4
# other
DHT_PIN2  = 24
DHT_PIN3  = 5
DHT_PIN4  = 6

#if (len(sys.argv) < 2):
#   raise  ValueError('Input arguments of mqtt channel temperature humidity not passed')

MOSQUITTO_HOST = '192.168.1.15'
MOSQUITTO_PORT = 1883
MOSQUITTO_TEMP_MSG = str('turtle/temp1') # Old channel name in here
MOSQUITTO_HUMI_MSG = str('turtle/humidity1') # Old channel name now passed by argument
# additional Sensor
MOSQUITTO_TEMP_MSG2 = str('turtle/temp2') # Old channel name in here
MOSQUITTO_HUMI_MSG2 = str('turtle/humidity2') # Old channel name now passed by argument
MOSQUITTO_TEMP_MSG3 = str('turtle/temp3') # Old channel name in here
MOSQUITTO_HUMI_MSG3 = str('turtle/humidity3') # Old channel name now passed by argument
MOSQUITTO_TEMP_MSG4 = str('turtle/temp4') # Old channel name in here
MOSQUITTO_HUMI_MSG4 = str('turtle/humidity4') # Old channel name now passed by argument
MOSQUITTO_BASE_TOPIC = str('turtle')
MOSQUITTO_LWT_TOPIC = MOSQUITTO_BASE_TOPIC[0] + '/LWT' #Create the last-will-and-testament topic
#print('Mosquitto Temp MSG {0}'.format(MOSQUITTO_TEMP_MSG))
#print('Mosquitto Humidity MSG {0}'.format(MOSQUITTO_HUMI_MSG))
#print('Mosquitto Temp MSG2 {0}'.format(MOSQUITTO_TEMP_MSG2)) # Second Sensor
#print('Mosquitto Humidity MSG2 {0}'.format(MOSQUITTO_HUMI_MSG2)) # Second Sensor
#print('Mosquitto Temp MSG3 {0}'.format(MOSQUITTO_TEMP_MSG3)) # Third Sensor
#print('Mosquitto Humidity MSG3 {0}'.format(MOSQUITTO_HUMI_MSG3)) # Third Sensor
#print('Mosquitto Temp MSG4 {0}'.format(MOSQUITTO_TEMP_MSG4)) # Fourth Sensor
#print('Mosquitto Humidity MSG4 {0}'.format(MOSQUITTO_HUMI_MSG4)) # Fourth Sensor
#print('Mosquitto LWT MSG {0}'.format(MOSQUITTO_LWT_TOPIC))

# How long to wait (in seconds) between measurements.
#print "Args length: " + str(len(sys.argv))
FREQUENCY_SECONDS      = 120

#if (len(sys.argv) > 7):
#	FREQUENCY_SECONDS = float(sys.argv[7])


print('Logging sensor measurements to {0} every {1} seconds.'.format('MQTT', FREQUENCY_SECONDS))
print('Press Ctrl-C to quit.')
print('Connecting to MQTT on {0}'.format(MOSQUITTO_HOST))
mqttc = mqtt.Client("python_pub")
mqttc.will_set(MOSQUITTO_LWT_TOPIC, payload='offline', qos=0, retain=True)
mqttc.connect(MOSQUITTO_HOST,MOSQUITTO_PORT, keepalive=FREQUENCY_SECONDS+10)
mqttc.publish(MOSQUITTO_LWT_TOPIC, payload='online', qos=0, retain=True)
try:

    while True:
        # Attempt to get sensor reading.
        humidity, temp1c = Adafruit_DHT.read(DHT_TYPE, DHT_PIN)
        time.sleep(1)
        print('Temperature 1: {0:0.2f} C'.format(temp1c))
        humidity2, temp2c = Adafruit_DHT.read(DHT_TYPE, DHT_PIN2) # Second Sensor
        time.sleep(1)
        print('Temperature 2: {0:0.2f} C'.format(temp2c))
        humidity3, temp3c = Adafruit_DHT.read(DHT_TYPE, DHT_PIN3) # Third Sensor
        time.sleep(1)
        print('Temperature 3: {0:0.2f} C'.format(temp3c))
        humidity4, temp4c = Adafruit_DHT.read(DHT_TYPE, DHT_PIN4) # Fourth Sensor
        print('Temperature 4: {0:0.2f} C'.format(temp4c))
        # Moved to Try logic
        #temp = (temp1c * 9/5) + 32
        #temp2 = (temp2c * 9/5) + 32
        #temp3 = (temp3c * 9/5) + 32
        #temp4 = (temp4c * 9/5) + 32

        # Skip to the next reading if a valid measurement couldn't be taken.
        # This might happen if the CPU is under a lot of load and the sensor
        # can't be reliably read (timing is critical to read the sensor).
        if humidity is None or temp1c is None or humidity2 is None or temp2c is None or humidity3 is None or temp3c is None or humidity4 is None or temp4c is None: # + Second Sensor
           time.sleep(4)
           continue

        currentdate = time.strftime('%Y-%m-%d %H:%M:%S')
        #print('Date Time:   {0}'.format(currentdate))
        #print('Temperature 1: {0:0.2f} C'.format(temp1c))
        #print('Temperature 1F: {0:0.2f} F'.format(temp))
        #print('Humidity 1:    {0:0.2f} %'.format(humidity))
        #print('Temperature 2: {0:0.2f} C'.format(temp2c)) # Second Sensor
        #print('Temperature 2F: {0:0.2f} F'.format(temp2)) # Second Sensor
        #print('Humidity 2:    {0:0.2f} %'.format(humidity2)) # Second Sensor
        #print('Temperature 3: {0:0.2f} C'.format(temp3c)) # Third Sensor
        #print('Temperature 3F: {0:0.2f} F'.format(temp3)) # Third Sensor
        #print('Humidity 3:    {0:0.2f} %'.format(humidity3)) # Third Sensor
        #print('Temperature 4: {0:0.2f} C'.format(temp4c)) # Fourth Sensor
        #print('Temperature 4F: {0:0.2f} F'.format(temp4)) # Fourth Sensor
        #print('Humidity 4:    {0:0.2f} %'.format(humidity4)) # Fourth Sensor
        # Publish to the MQTT channel
        try:
            # Check sensor before trying to avoid hanging (due to multiple sensors)
            ## new version
            # SENSOR 1
            if humidity is not None and temp1c is not None:
                temp = (temp1c * 9/5) + 32
                (result1,mid) = mqttc.publish(MOSQUITTO_TEMP_MSG,temp)
                time.sleep(1)
                (result2,mid) = mqttc.publish(MOSQUITTO_HUMI_MSG,humidity)
                time.sleep(1)
            else:
                print("Failed to retrieve data from sensor 1")
            # SENSOR 2
            if humidity2 is not None and temp2c is not None:
                temp2 = (temp2c * 9/5) + 32
                (result3,mid) = mqttc.publish(MOSQUITTO_TEMP_MSG2,temp2)
                time.sleep(1)
                (result4,mid) = mqttc.publish(MOSQUITTO_HUMI_MSG2,humidity2)
                time.sleep(1)
            else:
                print("Failed to retrieve data from sensor 2")
            # SENSOR 3
            if humidity is not None and temp1c is not None:
                temp3 = (temp3c * 9/5) + 32
                (result5,mid) = mqttc.publish(MOSQUITTO_TEMP_MSG3,temp3)
                time.sleep(1)
                (result6,mid) = mqttc.publish(MOSQUITTO_HUMI_MSG3,humidity3)
                time.sleep(1)
            else:
                print("Failed to retrieve data from sensor 3")
            # SENSOR 4
            if humidity is not None and temp1c is not None:
                temp4 = (temp4c * 9/5) + 32
                (result7,mid) = mqttc.publish(MOSQUITTO_TEMP_MSG4,temp4)
                time.sleep(1)
                (result8,mid) = mqttc.publish(MOSQUITTO_HUMI_MSG4,humidity4)
                time.sleep(1)
            else:
                print("Failed to retrieve data from sensor 4")
            # End if
            print('MQTT Updated result {0}, {1}, {2}, {3}, {4}, {5}, {6}, {7} '.format(result1,result2,result3,result4,result5,result6,result7,result8))
            #print 'MQTT Updated result {0} and {1}'.format(result3,result4)
            if result1 == 1 or result2 == 1 or result3 == 1 or result4 == 1 or result5 == 1 or result6 == 1 or result7 == 1 or result8 == 1:
                raise ValueError('Result for one message was not 0')

        except Exception,e:
            # Error appending data, most likely because credentials are stale.
            # Null out the worksheet so a login is performed at the top of the loop.
            print('Append error, logging in again: ' + str(e))
            continue

        # Wait 30 seconds before continuing
        print('Wrote a message to MQTT broker')
        time.sleep(FREQUENCY_SECONDS)

except Exception as e:
    print('Error connecting to the MQTT server: {0}'.format(e))
