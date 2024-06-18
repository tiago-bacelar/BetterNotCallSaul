from datetime import datetime
import sys

logging=True
timers = [datetime.now()]

def pushTimer():
    timers.append(datetime.now())

def getTimer():
    return f"{(datetime.now() - timers[-1]).total_seconds()}s"

def popTimer():
    ans = getTimer()

    if len(timers) == 1:
        raise "Invalid pop: there was nothing to pop"

    timers.pop()
    return ans

def log(msg: str):
    if logging:
        print(msg, file=sys.stderr)