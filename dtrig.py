from math import *

d2r = pi/180
r2d = 180/pi

def dsin(dang) :
    return sin(dang * d2r)

def dcos(dang) :
    return cos(dang * d2r)

def dtan(dang) :
    return tan(dang * d2r)

def dasin(s) :
    return r2d * asin(s)

def dacos(c) :
    return r2d * acos(c)

def datan(t) :
    return r2d * atan(t)

def datan2(x, y) :
    return r2d * atan2(x, y)
