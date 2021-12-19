# Turtle_Sensor

Update: The latest version changes the pin locations and adds 4 pins to turn +3.3v on before the sensor is queried. 

A handful of people showed interest in my Turtle_Sensor project so I thought I would share some details. 

Here are a few relevant photos of the project: https://imgur.com/a/G3dkZU8
        

> Warning: This post is a quick and dirty overview, so don't expect a perfect start to finish tutorial. This is more about how I made the project work and some of the things I learned that may be useful for others. I will try to make it as coherent as possible, but apologize in advance if its not.

---
--
For anyone interested in the tortoise pen itself: 
--
I finished the basement this year and put "water proof" laminate flooring down on concrete. To protect the floor and baseboard, I used old (and well vacuumed) carpet backing side up. The carpet was cut 3 inches longer on all sides and rolled up the wall to prevent scuffing. This also helped insulate the pen. I bought 20'x30' blue tarp and folded it to fit the room (extra length on each side as well). This resulted in a 4 layer barrier between the carpet. I then ripped 4x4 1/2 inch ply down to 2x4 and a few 2x2 sheets. Not much engineering here, simply screwed a 2x4 and 2 sheets of ply together to make a corner, rinse and repeat. Concrete blocks were placed on the open side but honestly aren't necessary in retrospect. The tarp and carpet created a padding between the wall and ply so the tortoise can ram into it and not damage the wall. I did find that the tortoise was starting to rub holes in the tarp a few weeks into living there, so I cut more plywood into triangles and shoved them into the corners. ymmv, but overall a very cheap build.

---

> TLDR: I used python to query the DHT22 sensors and send the results to openhab with MQTT. That gave me the ability to build a dashboard of real time results, but did not show the historical data. I set up ELK in docker and installed Filebeats on the Openhab server. The filebeats forwarded all of my /var/log/openhab2/events.log to ELK. On the ELK container, I customized a logstash config to listen on port 5014 (because ports under 1000 require root) and added logic to parse out openhab item updates. I also customized it so any OH item with "Turtle_Sensor_" would duplicate output the log into a second index so I wouldn't have my dimmer updates showing up in my turtle dashboards within kibana.


    [Sensors]--[PI]--(mqtt)-->[OpenHab2]--[HABPanel WebUI]
                                             |
    				                   [ FileBeats ]
    									     |
                                             |-> [Logstash]-[Elastic]-[Kibana] 

Its easiest to think of the project in 3 chunks; Get the sensor data, save the results somewhere, view the results. The process will vary based on the desired outcome and level of effort. I won't be able to document every single way to do it, so I will just explain what I did and explain alternatives when I remember.

===
What will you need:
===
--
(Easy Mode)
--

+ Time = priceless
+ Raspberry Pi = $35-60 (ymmv)
+ -- You can get away with using Pi0W's if you only plan to use them for sensor->mqtt
+ DHT22 sensor = $11.98 for x2 (these don't require resistors)
+ -- https://www.amazon.com/gp/product/B073F472JL

--
(Creative mode)
--

+ Old wire/ethernet = $free
+ soldering stuff = $not-so-free
+ Perma-Proto board = $5 
+ -- https://www.adafruit.com/product/2310
+ Terminals = $4 for x5
+ -- https://www.adafruit.com/product/725

--
(Rabbit hole)
--

+ Home hypervisor/server = $LOL (see r/homelab if you are lost) 
+ -- Proxmox or other = $free
+ -- OpenHab = $free (and some experience using it, I won't go into detail)
+ -- Docker and/or ELK $free (ELK in docker is easier than setting it up manually imo)
+ more sensors to complicate things even more

===
Hardware setup: 
===
Make your life easy, start with 1 sensor and add more once it works. These DHT22 sensors can use +3.3v or +5v. I originally set up 2 and plugged them directly into the 3.3v, ground, and GPIO pins 4 and 24. 

=== 
Software setup: 
===
There are a few projects out there that explain how to set up DHT22 sensors. Google is your friend. EG: https://github.com/janw/dht22-mqtt-daemon 

Because my goal was to get the sensor data into openhab2, I started with this python script to do MQTT: 
https://github.com/psyciknz/OpenHAB-Scripts/blob/master/mqtt.dhtsensor.py

You can comment the "send MQTT" parts out of the script and simply print the sensor data or pipe it into a log file on the Pi and view it manually if you wanted. 

I manually ran the script with "python mqtt.channel.py <temp topic> <humidity topic> <gpio pin> <optional update frequency>" on the pi and watched the verbos output to ensure the sensors and MQTT worked. After I got everything working, I set static variables and configured a service (more on that later).

===
OpenHAB config:
===

In PaperUI, I simply enabled the MQTT binding in OpenHAB and set up a Thing called "Turtle_Sensor". From there, I added channels that listened for turtle/temp1, turtle/humidity1,turtle/temp2, turtle/humidity2, etc. I found that each channel/item should be set to Number. The number type should be temp for temp and dimensionless for humidity. 

The temp comes in as celsius so I converted the result to Fahrenheit inside the python script. I spent far too much time trying to convert C to F in openhab and **if you take nothing else from this post, at least remember: do conversions in python on the pi.** 

Regardless, the sensor results will show up in MQTT as a float (nn.nnnnnnn... ). I didn't find a good way to truncate the decimal in paperui but it was easy to do in HABPanel (Dummy widget. Suffix: °F Format: %.2f).

===
Complicating the project: Hardware
===
Eventually I used Perma-proto board to solder on screw terminals to make swapping/adding sensors easier. From there I added 2 more sensors onto pins GPIO 5 and 6. I chose the perma-proto because I could add a bunch of terminals that share the 3.3v and have room for more. A breadboard would work here too. Eventually, I may move to a custom PCB.

I also added a 7 inch HDMI monitor I had laying around. Any screen will do, if you want to display the dashboard.

===
Complicating the project: Software
===

I had to modify the python script (above) to allow 2-4 sensors. This can be done a lot of different ways, some being more elegant than others. I just duped all of the vars and commands for each sensor. I thought about doing a foreach loop but then got lazy. See all of the script changes in the git I put up here: https://github.com/kulithian/Turtle_Sensor/blob/main/static.mqtt.dhtsensor.py

Additionally, I set the MQTT input variables to static items within the script to prevent the need for input variables. After testing, I created a service that calls "python ./home/pi/static.mqtt.dhtsensor.py". I found that the script would occasionally throw an error and the service would stop and not restart, so I also set a cron job to restart the service itself every midnight, you know, instead of fixing the script or whatever. There was some fiddling with permissions and chmod -x that I can't remember off the top of my head, so google is your friend if you have issues with service not launching. 

--
ELK:
--


Because I wasn't happy with how much time I already spent on the project, I decided I want historical data as well. I installed filebeats on the openhab2 server and configured it to ship /var/log/openhab2/events.log to a new docker vm running ELK. I added port 5014:5014 to the docker run command so I had a unique port for the next portion.

There are plenty of documents on how to ship logs with filebeats to logstash but I included my custom tweaks in my git:


**(On the Openhab server)**

- sudo nano /etc/filebeat/filebeat.yml -> see changes here: https://github.com/kulithian/Turtle_Sensor/blob/main/FileBeat-Openhab-Changes

**(On the Docker elk container)**

- Connecting to the ELK stack in docker from putty: sudo docker exec -it <container name> /bin/bash 
- nano /etc/logstash/conf.d/91-openhab-input.conf -> see changes here: https://github.com/kulithian/Turtle_Sensor/blob/main/91-openhab-input.conf 

The above tweaks resulted in all openhab updates (zwave dimmers, Turtle_Sensor, unifi bridges, etc) to show up in ELK via the filebeats-yyyy.mm.dd index . Additionally, anything with "turtle_sensor_" in the name is duplicated to a turtle_sensor-yyy.mm.dd index. This is far easier than adding filters on Kibana visualizations/dashboards.

**Note:** I frequently ran into ELK index converting my "number" into "strings" despite setting %{NUMBER:temp:float}. I think it is important to PURGE (delete all of the data) in the index from ES after changing the logstash config, otherwise the index uses old data (if it was a string at one point) to set the data type, and string may be a general wildcard. Im no expert so take that with a grain of salt. This is part of the reason why I forked sensor data to a new index.

With that said, if a sensor value is exactly the same as it was, the Openhab events.log file does not log the latest MQTT message for that sensor (since the item value does not change). You will see something like "Temp1 changed from x to y, Temp 3 changed from x to y". (but no temp 2). This results in missing data on the Kibana dashboard (due to dashboards being dependent on timelines). I may fix this by using filebeats on the Pi instead of openhab in the future, or forcing possibly the value to update in OpenHab no matter what.

--
Kiosk display:
---
Lastly, setting up a Pi (rasp lite) as a Chromium Kiosk:
https://blog.r0b.io/post/minimal-rpi-kiosk/

I used the instructions above to force the Pi that is collecting the sensor data to auto login as pi, then startx which launches chromium in full screen. Works great out of the box. I removed the incognito flag because openhab needs to save/cache the dashboard configuration (using server display and not local display).


I think that's about it. Hopefully that made sense and was helpful in some capacity. If not, leave a comment and I can try to answer any questions you have.
