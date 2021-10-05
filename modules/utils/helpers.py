import time

def getTimeMillis():
    round(time.time() * 1000)

def getTimeElapsed(then):
    return then - getTimeMillis()