#!/usr/bin/env python
#-*- coding: utf-8 -*-

import signal, time, sys, datetime, os, argparse
import subprocess as sub

from vfd import Vfd
#from weather import Weather
from acmepins import GPIO

# VFD configuration
#===================

v = Vfd()
dim_delay = "\x01" # 1 minute delay
print u"Initiated VFD"

# Signals handlers
#==================

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

# Servers list
#==============

servers = (("bbbforum", u"bf"), ("bbbdata", u"bd"), ("odroid", u"od"), ("skymule", u"sm"), ("domdroid", u"dd"))

# Pushbutton configuration
#==========================

#def pb_handler():
#    v.setDisplay(duration=dim_delay)

pb = GPIO("PA24", "INPUT") # update button
#pb = GPIO("PC17", "INPUT") # on board PB
#pb.set_edge("falling", pb_handler)
#print u"Started PB edge detection"

# Functions
#===========

def check_wifi():
    """Check if we have an IP address on wlan0.
    """
    output = sub.check_output("/sbin/ifconfig wlan0 | grep inet\ addr | wc -l", shell=True)
    if output == "1\n":
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

def update_time():
    now = datetime.datetime.now()
    v.write(u"{}".format(now.strftime("%H:%M")), x=15, y=0)

# Main loop
#===========

def main(args):
    """Program initiation and main loop.
    """
    v.clear()
    v.setLineWrap(True)
    v.setBrightness(25)
    v.setDisplay(duration=dim_delay)
    v.write(u"Servers: ...", x=0, y=0)
    v.write(u"Failed: ...", x=0, y=1)

    if not args.no_cal:
        import o365_client
        rr_cal = 36000 # in 1/10s (1 hour)
        j = rr_cal
    else:
        print u"Execution sans calendrier"

#    w = Weather()
#    last_weather = datetime.datetime.now()
#    temp = w.get_temp()
#    interval = datetime.timedelta(minutes=15) # Every 15 minutes
#    v.write(u"Temp.: ...", x=0, y=2)

    rr_normal = 300 # in 1/10s (30 sec)
    rr_failed = 30 # in 1/10s (3 sec)
    refresh_rate = rr_normal
    i = refresh_rate

    vfd_on = False
    print "Nanny started, entering loop"

    while True:
        i += 1

        if i >= refresh_rate:

            update_time()

            if check_wifi():
                if args.verbose:
                    print u"Updating servers status (pings)"

                i = 0
                if not args.no_cal:
                    j += refresh_rate
                ok = 0
                failed = []

                for s in servers:
                    if check_ping(s[0]):
                        ok += 1
                    else:
                        failed.append(s[1])

                v.write(u"{}/{}".format(ok, len(servers)), x=9, y=0)
                v.erase(x=20, y=1, l=13)
                v.move(x=8, y=1)

                if len(failed):
#                    v.setDisplay(duration=dim_delay)
                    print u"Servers failed: {}".format(failed)
                    refresh_rate = rr_failed
                    for x in range(len(failed)):
                        v.write(failed[x])
                        if (x+1) < len(failed):
                            v.write(u",")
                else:
                    refresh_rate = rr_normal
                    v.write(u"N/A")

#                if datetime.datetime.now() > (last_weather + interval):
#                    if w.owm.is_API_online():
#                        temp = w.get_temp(update=True)
#                        last_weather = datetime.datetime.now()
#                        v.erase(x=7, y=2, l=12)
#                        try:
#                            v.write("{}\xb2C".format(temp[0]), x=7, y=2)
#                        except IndexError:
#                            v.write("?\xb2C", x=7, y=2)

            else:
                print u"Wifi down, skipping pings"

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

        if not args.no_cal and j >= rr_cal:
            if check_wifi():
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
#                    print u"Next event: {} @ {}:{}".format(first_event.getSubject(), hour, mins)

                else:
                    print u"No upcoming event in the next 24h"
            else:
                print u"Wifi down, skipping calendar update"

        if pb.get() != 0:
            print u"Pushbutton pressed, turning VFD on for 1 minute"
            v.setDisplay(duration=dim_delay)

        time.sleep(0.1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Supervision serveurs et un peu plus")
    parser.add_argument("-v",
                        "--verbose",
                        action="store_true",
                        default=False,
                        help=u"Imprime davantage d'information sur l'execution du programme.")
    parser.add_argument("--no-cal",
                        action="store_true",
                        default=False,
                        help=u"Execute le programme sans le calendrier Outlook365.")
    args = parser.parse_args()
    main(args)

