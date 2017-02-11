#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time
from O365 import Schedule

class Client:

    def __init__(self, username=None, password=None):
        config = {}
        execfile("credentials.txt", config)
        if username is None:
            self.username = config["username"]
        else:
            self.username = username
        if password is None:
            self.password = config["password"]
        else:
            self.password = password

        self.schedule = Schedule((self.username, self.password))

        try:
            self.result = self.schedule.getCalendars()
            print 'Fetched calendars for',self.username,'was successful:',self.result
        except:
            print 'Login failed for',self.username

    def getEvents(self):
        for cal in self.schedule.calendars:
            end = time.time()
            end += 3600*24*7
            end = time.gmtime(end)
            end = time.strftime(cal.time_string,end)
            cal.getEvents(end=end)
            print u"Calendar \"{}\":".format(cal.getName())
            for e in cal.events:
                print u" [{}] {}".format(e.getStart(), e.getSubject())

if __name__ == "__main__":
    client = Client()
    client.getEvents()
