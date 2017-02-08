# -*- coding: utf-8 -*-

import pyowm

#KEY = "c613d7fb9e2ec98823f8bbb8de7befc4" # default
KEY = "de79ebae33363e14394e058db03512aa" # nanny

class Weather:

    def __init__(self, location="Quebec,ca"):
        self.owm = pyowm.OWM(KEY)
        self.location = location
        self.get_obs()

    def get_obs(self):
        self.obs = self.owm.weather_at_place(self.location)

    def get_temp(self, update=False):
        if update:
            self.get_obs()
        w = self.obs.get_weather()
        return w.get_temperature("celsius")["temp"], w.get_status()

    def get_id(self):
        self.reg = self.owm.city_id_registry()
        print self.reg.ids_for(self.location)
        print self.reg.locations_for(self.location)

if __name__ == "__main__":
    w = Weather()
    print "Temp.: {} C".format(w.get_temp())
    we = w.obs.get_weather()
    print we.get_temperature()
    w.get_id()
