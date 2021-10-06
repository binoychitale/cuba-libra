import time


def getTimeMillis():
    return round(time.time() * 1000)


def getTimeElapsed(then):
    return then - getTimeMillis()
