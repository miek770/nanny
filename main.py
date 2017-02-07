#!/usr/bin/env python
#-*- coding: utf-8 -*-

import signal, time, sys

from vfd import Vfd
from ping import check_ping

v = Vfd()
serveurs = ("bbbforum", "bbbdata", "odroid", "skymule")

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
    v.setLineWrap(True)
    v.setBrightness(25)
    v.setDisplay()
    v.write("Servers: ...")
    print "Nanny started"
    while True:
        ok = 0
        failed = []
        for s in serveurs:
            if check_ping(s):
                ok += 1
            else:
                failed.append(s)
        v.write("{}/{}".format(ok, len(serveurs)), x=9, y=0)
        if len(failed):
            v.write("Failed: {}".format(failed), x=0, y=1)
        time.sleep(30)

if __name__ == "__main__":
    main()

