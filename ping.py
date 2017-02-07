#-*- coding: utf-8 -*-

import os

def check_ping(hostname):

    response = os.system("ping -c 1 " + hostname + " > /dev/null")

    # and then check the response...
    if response == 0:
        return True
    else:
        return False

