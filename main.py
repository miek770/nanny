#!/usr/bin/env python
#-*- coding: utf-8 -*-

import signal, time, sys, datetime, os

from vfd import Vfd
#from weather import Weather
from acmepins import GPIO
import o365_client

v = Vfd()
dim_delay = "\x01" # 1 minute delay
print u"Initiated VFD"

def sigint_handler(signum, frame):
    print u"CTRL+C captured, exiting."
    v.clear()
    v.ser.close()
    sys.exit(signum)

def sigterm_handler(signum, frame):
    print u"SIGTERM received, exiting."
    v.clear()
    v.ser.close()
    sys.exit(0) # SIGTERM (15) is reported as an error by systemctl

signal.signal(signal.SIGINT, sigint_handler)
signal.signal(signal.SIGTERM, sigterm_handler)
print u"Initiated signals handlers"

servers = (("bbbforum", u"bf"), ("bbbdata", u"bd"), ("odroid", u"od"), ("skymule", u"sm"))

#def pb_handler():
#    v.setDisplay(duration=dim_delay)

pb = GPIO("PA24", "INPUT") # update button
#pb = GPIO("PC17", "INPUT") # on board PB
#pb.set_edge("falling", pb_handler)
#print u"Started PB edge detection"

def check_wifi():
    """Check if we have an IP address on wlan0.
    """
    response = os.system("/sbin/ifconfig wlan0 | grep inet\ addr | wc -l")
    if response == 1:
        return True
    else:
        return False

def check_ping(hostname):
    """Check if "hostname" replies to a ping.
    """
    response = os.system("ping -c 1 " + hostname + " > /dev/null")
    if response == 0:
        return True
    else:
        return False

def main():
    v.clear()
    v.setLineWrap(False)
    v.setBrightness(25)
    v.setDisplay(duration=dim_delay)
    v.write(u"Servers: ...", x=0, y=0)
    v.write(u"Failed: ...", x=0, y=1)

#    w = Weather()
#    last_weather = datetime.datetime.now()
#    temp = w.get_temp()
#    interval = datetime.timedelta(minutes=15) # Every 15 minutes
#    v.write(u"Temp.: ...", x=0, y=2)

    rr_cal = 36000 # in 1/10s (1 hour)
    rr_normal = 300 # in 1/10s (30 sec)
    rr_failed = 30 # in 1/10s (3 sec)
    refresh_rate = rr_normal
    i = refresh_rate
    j = rr_cal

    vfd_on = False
    print u"Nanny started, entering loop"

    while True:
        i += 1
        if i >= refresh_rate:
#            print u"Refreshing server status"
            i = 0
            j += refresh_rate
            ok = 0
            failed = []

            for s in servers:
                if check_ping(s[0]):
                    ok += 1
                else:
                    failed.append(s[1])

            v.write(u"{}/{}".format(ok, len(servers)), x=9, y=0)
            v.erase(x=8, y=1, l=len(servers)*3-1)
            v.move(x=8, y=1)

            if len(failed):
#                v.setDisplay(duration=dim_delay)
                print u"Servers failed: {}".format(failed)
                refresh_rate = rr_failed
                for x in range(len(failed)):
                    v.write(failed[x])
                    if (x+1) < len(failed):
                        v.write(u",")
            else:
                refresh_rate = rr_normal
                v.write(u"N/A")

#            if datetime.datetime.now() > (last_weather + interval):
#                if w.owm.is_API_online():
#                    temp = w.get_temp(update=True)
#                    last_weather = datetime.datetime.now()
#                    v.erase(x=7, y=2, l=12)
#                    try:
#                        v.write("{}\xb2C".format(temp[0]), x=7, y=2)
#                    except IndexError:
#                        v.write("?\xb2C", x=7, y=2)

            now = datetime.datetime.now()
            if (now.hour >= 6 and now.hour < 8) or (now.hour >= 20 and now.hour <= 22):
                if not vfd_on:
                    print u"Scheduled VFD on"
                    v.setDisplay(True)
                    vfd_on = True
            else:
                if vfd_on:
                    print u"Scheduled VFD off"
                    v.setDisplay(True, duration=dim_delay)
                    vfd_on = False

        if j >= rr_cal:
            print u"Refreshing calendar"
            j = 0
            first_event = o365_client.Client().firstEvent
            v.erase(x=0, y=2, l=19)
            v.erase(x=0, y=3, l=19)
            if first_event is not None:
                hour = first_event.getStart().tm_hour - time.altzone/(60**2) - time.daylight
                mins = first_event.getStart().tm_min
                if mins > 0:
                    v.write(u"1st event at {}:{}".format(hour, mins), x=0, y=2)
                else:
                    v.write(u"1st event at {}:00".format(hour), x=0, y=2)
                v.write(u"{}".format(first_event.getSubject()[:20]), x=0, y=3)
#                print u"Next event: {} @ {}:{}".format(first_event.getSubject(), hour, mins)

            else:
                print u"No upcoming event in the next 24h"

        if pb.get() != 0:
            print u"Pushbutton pressed, turning VFD on for 1 minute"
            v.setDisplay(duration=dim_delay)

        time.sleep(0.1)

if __name__ == "__main__":
    main()

