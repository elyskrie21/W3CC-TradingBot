
import datetime

COLOR_RESET = "\033[0;0m]"
COLOR_GREEN = "\033[0;32m]"
COLOR_RED = "\033[1;31m]"
COLOR_BLUE = "\033[1;34m]"
COLOR_WHITE = "\033[1;37m]"

def myLogger(msg, logFile):
        timestamp = datetime.datetime.now().strftime("%b %d %Y %H:%M:%S ")
        s = "[%s] %s:%s %s" % (timestamp, COLOR_WHITE, COLOR_RESET, msg)
        try:
            f = open(logFile, "a")
            f.write(s + "\n")
            f.close()
        except:
            pass