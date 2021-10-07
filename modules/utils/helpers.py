import time
from typing import List


def getTimeMillis():
    return round(time.time() * 1000)


def getTimeElapsed(then):
    return then - getTimeMillis()
