#!/usr/bin/env python
#-*- coding: utf-8 -*-

import signal, time, sys, datetime

from vfd import Vfd
from ping import check_ping
from weather import Weather

v = Vfd()
servers = (("bbbforum", "bf"), ("bbbdata", "bd"), ("odroid", "od"), ("skymule", "sm"))

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

def main():
    v.clear()
    v.setLineWrap(False)
    v.setBrightness(25)
    v.setDisplay()
    v.write("Servers: ...", x=0, y=0)
    v.write("Failed: ...", x=0, y=1)

    w = Weather()
    last_weather = datetime.datetime.now()
    temp = w.get_temp()
    interval = datetime.timedelta(15*60)

    print "Nanny started"
    while True:
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
            for x in range(len(failed)):
                v.write(failed[x])
                if (x+1) < len(failed):
                    v.write(",")
        else:
            v.write("N/A")

        time.sleep(30)

if __name__ == "__main__":
    main()

