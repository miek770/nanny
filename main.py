#!/usr/bin/env python
#-*- coding: utf-8 -*-

import signal, time, sys, datetime

from vfd import Vfd
from ping import check_ping
#from weather import Weather
from acmepins import GPIO

v = Vfd()
dim_delay = "\x01" # 1 minute delay
print "Initiated VFD"

def sigint_handler(signum, frame):
    print "CTRL+C captured, exiting."
    v.clear()
    v.ser.close()
    sys.exit(signum)

def sigterm_handler(signum, frame):
    print "SIGTERM received, exiting."
    v.clear()
    v.ser.close()
    sys.exit(0) # SIGTERM (15) is reported as an error by systemctl

signal.signal(signal.SIGINT, sigint_handler)
signal.signal(signal.SIGTERM, sigterm_handler)
print "Initiated signals handlers"

servers = (("bbbforum", "bf"), ("bbbdata", "bd"), ("odroid", "od"), ("skymule", "sm"))

#def pb_handler():
#    v.setDisplay(duration=dim_delay)

pb = GPIO("PC17", "INPUT") # on board PB
#pb.set_edge("falling", pb_handler)
#print "Started PB edge detection"

def main():
    v.clear()
    v.setLineWrap(False)
    v.setBrightness(25)
    v.setDisplay(duration=dim_delay)
    v.write("Servers: ...", x=0, y=0)
    v.write("Failed: ...", x=0, y=1)

#    w = Weather()
#    last_weather = datetime.datetime.now()
#    temp = w.get_temp()
#    interval = datetime.timedelta(15*60) # Every 15 minutes
#    v.write("Temp.: ...", x=0, y=2)

    i = 0
    rr_normal = 300 # in 1/10s
    rr_failed = 30 # in 1/10s
    refresh_rate = rr_normal
    print "Nanny started, entering loop"

    while True:
        i += 1
        if i >= refresh_rate:
            i = 0
            ok = 0
            failed = []

            for s in servers:
                if check_ping(s[0]):
                    ok += 1
                else:
                    failed.append(s[1])

            v.write("{}/{}".format(ok, len(servers)), x=9, y=0)
            v.erase(x=8, y=1, l=len(servers)*3-1)
            v.move(x=8, y=1)

            if len(failed):
#                v.setDisplay(duration=dim_delay)
                refresh_rate = rr_failed
                for x in range(len(failed)):
                    v.write(failed[x])
                    if (x+1) < len(failed):
                        v.write(",")
            else:
                refresh_rate = rr_normal
                v.write("N/A")

#            if datetime.datetime.now() > (last_weather + interval):
#                if w.owm.is_API_online():
#                    temp = w.get_temp(update=True)
#                    last_weather = datetime.datetime.now()
#                    v.erase(x=7, y=2, l=12)
#                    try:
#                        v.write("{}\xb2C".format(temp[0]), x=7, y=2)
#                    except IndexError:
#                        v.write("?\xb2C", x=7, y=2)

        if pb.get() == 0:
            v.setDisplay(duration=dim_delay)

        time.sleep(0.1)

if __name__ == "__main__":
    main()

