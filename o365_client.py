#!/usr/bin/env python
# -*- coding: utf-8 -*-

import time, json
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
            self.firstEvent = self.getFirstEvent()
        except:
            print 'Login failed for',self.username
            self.firstEvent = None

    def getFirstEvent(self):
        first = None
        for cal in self.schedule.calendars:
            end = time.time()
#            end += 3600*24*7 # Next 7 days
            end += 3600*24 # Next 24h
            end = time.gmtime(end)
            end = time.strftime(cal.time_string,end)
            cal.getEvents(end=end)
#            events = []
#            print u"Calendar \"{}\":".format(cal.getName())
#            for e in cal.events:
#                print u" [{}] {}".format(e.getStart(), e.getSubject())
#                events.append(e.fullcalendarioJson())

#            print json.dumps(events,sort_keys=True,indent=4,ensure_ascii=False)

            if len(cal.events):
                if first is None:
                    first = cal.events[0]
                for e in cal.events:
                    if e.getStart() < first.getStart():
                        first = e

#        if first is not None:
#            hour = first.getStart().tm_hour - time.altzone/(60**2) - time.daylight
#            mins = first.getStart().tm_min
#            if mins >0:
#                print u"First event on the schedule: {} @ {}:{}".format(first.getSubject(), hour, mins)
#            else:
#                print u"First event on the schedule: {} @ {}:00".format(first.getSubject(), hour)

        if first is not None:
            return first
        else:
            return None
