#-*- coding: utf-8 -*-

import serial
from unidecode import unidecode

class Vfd:
    def __init__(self, port="/dev/ttyS1", baud=19200):
        self.ser = serial.Serial(port, baud)
        self.remember = False
        self.coord = list()
        self.coord.append("\x01")#0
        self.coord.append("\x02")#1
        self.coord.append("\x03")#2
        self.coord.append("\x04")#3
        self.coord.append("\x05")#4
        self.coord.append("\x06")#5
        self.coord.append("\x07")#6
        self.coord.append("\x08")#7
        self.coord.append("\x09")#8
        self.coord.append("\x0A")#9
        self.coord.append("\x0B")#10
        self.coord.append("\x0C")#11
        self.coord.append("\x0D")#12
        self.coord.append("\x0E")#13
        self.coord.append("\x0F")#14
        self.coord.append("\x10")#15
        self.coord.append("\x11")#16
        self.coord.append("\x12")#17
        self.coord.append("\x13")#18
        self.coord.append("\x14")#19
        self.coord.append("\x15")#20

        self.width = 20
        self.height = 4

        self.setRemember(True)
        self.setDisplay(True)
        self.setAutoScroll(False)
        self.setLineWrap(False)
        self.blink(False)

    # Écrit le texte à l'endroit spécifié
    def write(self, message, x=None, y=None):
#        l = len(message)
#        self.move(x+l, y)
        # Efface le texte actuel
#        for i in range(l):
#            self.backspace()
#        self.ser.write(message[:l])
        if x is not None and y is not None:
            self.move(x, y)
        self.ser.write(unidecode(message))

    def erase(self, x, y, l):
        self.move(x+l, y)
        for i in range(l):
            self.ser.write("\x08")

    # Écrit une nouvelle ligne au complet
    def writeLine(self, line, message):
        if len(message)>20:
            self.move(0,line)
            self.ser.write(message[:20])
        else:
            self.move(19,line)
            for i in range(19	):
                self.backspace()
            self.ser.write(message)

    def clear(self):
        self.ser.write("\x0C")

    def enter(self):
        self.ser.write("\x0D")

    def lineFeed(self):
        self.ser.write("\x0A")

    def backspace(self):
        self.ser.write("\x08")

    def setAutoScroll(self, state):
        if not self.remember:
            self.setRemember(True)
        if state:
            self.ser.write("\xFE\x51")
        else:
            self.ser.write("\xFE\x52")

    def clearScreen(self):
        self.ser.write("\xFE\x58")

    def setStartupScreen(self, message):
        if not self.remember:
            self.setRemember(True)
        self.ser.write("\xFE\x40" + str(message))

    def setLineWrap(self, state):
        if not self.remember:
            self.setRemember(True)
        if state:
            self.ser.write("\xFE\x43")
        else:
            self.ser.write("\xFE\x44")

    def move(self, x, y):
        if x > self.width:
            x = self.width
        if y > self.height:
            y = self.height

        try:
            self.ser.write("\xFE\x47" + self.coord[x] + self.coord[y])
        except ValueError:
            self.home()

    def home(self):
        self.ser.write("\xFE\x48")

    def back(self):
        self.ser.write("\xFE\x4C")

    def forward(self):
        self.ser.write("\xFE\x4D")

    def blink(self, state):
        if not self.remember:
            self.setRemember(True)
        if state:
            self.ser.write("\xFE\x53")
        else:
            self.ser.write("\xFE\x54")

    def setGPO(self, out, state):
        if state:
            self.ser.write("\xFE\x56" + str(int(out)))
        else:
            self.ser.write("\xFE\x57" + str(int(out)))

    def setStartupGPO(self, out, state):
        if not self.remember:
            self.setRemember(True)
        if state:
            self.ser.write("\xFE\xC3" + str(int(out)) + "1")
        else:
            self.ser.write("\xFE\xC3" + str(int(out)) + "0")

    def setDisplay(self, state=True, duration="\x00"):
        if not self.remember:
            self.setRemember(True)
        if state:
            self.ser.write("\xFE\x42{}".format(duration))
        else:
            self.ser.write("\xFE\x46")

    def setBrightness(self, brightness):
        if brightness in range(0,26):
            self.ser.write("\xFE\x91\x03")
        elif brightness in range(26,51):
            self.ser.write("\xFE\x91\x02")
        elif brightness in range(51,76):
            self.ser.write("\xFE\x91\x01")
        elif brightness in range(76,101):
            self.ser.write("\xFE\x91\x00")

    def setRemember(self, state=True):
        if state:
            self.ser.write("\xFE\x931")
            self.remember = True
        else:
            self.ser.write("\xFE\x930")
            self.remember = False
