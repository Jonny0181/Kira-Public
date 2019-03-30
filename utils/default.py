import time


def timetext(name):
    return "{}_{}.txt".format(name, int(time.time()))


def date(target):
    return target.strftime("%d %B %Y, %H:%M")
