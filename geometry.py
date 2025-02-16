#coding:utf-8

from __future__ import annotations
import numpy as np
import scipy
from numpy import linalg
from typing import Self
from dtrig import *
from math import *

SMALL = 1e-9

#
# Useful stand-alone functions
#

def hypot(x: float, y: float) -> float:
    return sqrt(x*x + y*y)

def hypot2(x: float, y: float) -> float:
    return x*x + y*y

def sign(x: float) -> float :
    return -1 if x<0 else 1

def dist(x0: float, y0: float, x1: float, y1: float) -> float:
    return sqrt(dist2(x0, y0, x1, y1))

def dist2(x0: float, y0: float, x1: float, y1: float) -> float:
    dx = x1-x0
    dy = y1-y0
    return dx*dx + dy*dy

def cosine_rule(l1: float, l2: float, opposite: float) -> float:
    result = dacos((l1*l1 + l2*l2 - opposite*opposite) / (2*l1*l2))
    if result < -360:
        print(f'cosine_rule {l1} {l2} {opposite}')
    return result

def included_angle(x0, y0, x1, y1, x2, y2) :
    a2 = dist2(x0, y0, x1, y1)
    b2 = dist2(x0, y0, x2, y2)
    c2 = dist2(x1, y1, x2, y2)
    return dacos((a2+b2-c2)/(2*sqrt(a2*b2)))

def equal(x1: float, x2: float) -> bool:
    diff = abs(x1 - x2)
    return diff < SMALL or diff / (max(abs(x1), abs(x2)) or 1.0) < SMALL

#
# Point2D - represents a 2D point
#

class Point2D:

    def __init__(self, x: float | np.ndarray=0.0, y: float=0.0):
        if isinstance(x, np.ndarray):
            self.p = x
        else:
            self.p = np.array([float(x), float(y)], dtype=np.float64)

    def clean(self) -> Self:
        return Point2D(np.round(self.p, 3))
        
    def __str__(self) -> str:
        c = self.clean()
        return f'(x={c.x():.3f} y={c.y():.3f})'

    def __add__(self, other) -> Self:
        if isinstance(other, Point2D):
            return Point2D(np.add(self.p, other.p))
        else:
            return Point2D(np.add(self.p, other))

    def __sub__(self, other) -> Self:
        if isinstance(other, Point2D):
            return Point2D(np.subtract(self.p, other.p))
        else:
            return Point2D(np.subtract(self.p, other))

    def __mul__(self, x: float) -> Point2D:
        return Point2D(np.multiply(self.p, x))

    def __truediv__(self, x: float) -> Point2D:
        return Point2D(np.divide(self.p, x))

    def __eq__(self, other: Point2D) -> bool:
        return equal(self.x(), other.x()) and equal(self.y(), other.y())

    def __ne__(self, other: Point2D) -> bool:
        return not (self==other)

    def x(self) -> float:
        return self.p[0]

    def y(self) -> float:
        return self.p[1]

    def length(self) -> float:
        return hypot(self.x(), self.y())

    def angle(self) -> float:
        return datan2(self.x(), self.y())

    def reflect_x(self) -> Point:
        return Point2D(self.x(), -self.y())

    def reflect_y(self) -> Self:
        return Point2D(-self.x(), self.y())

    def dist(self, other: Point2D) -> float:
        return sqrt(self.dist2(other))

    def dist2(self, other: Point2D) -> float:
        return np.sum(np.square(self - other).p)

    @staticmethod
    def from_polar(r: float, theta: float) -> Self:
        return Point2D(dsin(theta), dcos(theta)) * r 

#
# Point class - represents a 3D point, with a fourth value, always 1, to
# facilitate computing transforms
#

class Point:

    def __init__(self, x: float | np.ndarray=0.0, y: float=0.0, z: float=0.0):
        if isinstance(x, np.ndarray):
            self.p = x
            self.p[3] = 1
        else:
            self.p = np.array([float(x), float(y), float(z), 1.0], dtype=np.float64)

    def copy(self) -> Self:
        return Point(self.p.copy())

    def clean(self) -> Self:
        return Point(np.round(self.p, 3))
        
    def __str__(self) -> str:
        c = self.clean()
        return f'(x={c.x():.3f} y={c.y():.3f} z={c.z():.3f})'

    def __neg__(self) -> Self:
        return Point((-self.p))

    def __add__(self, other) -> Self:
        if isinstance(other, Point):
            return Point(np.add(self.p, other.p))
        else:
            return Point(np.add(self.p, other))
        
    def __sub__(self, other) -> Self:
        if isinstance(other, Point):
            return Point(np.subtract(self.p, other.p))
        else:
            return Point(np.subtract(self.p, other))

    def __eq__(self, other: Point2D) -> bool:
        return (equal(self.x(), other.x())
                and equal(self.y(), other.y())
                and equal(self.z(), other.z()))

    def __ne__(self, other: Point) -> bool:
        return not (self==other)
    
    def __mul__(self, other: float) -> Self:
        return Point(np.multiply(self.p, other))
    
    def __truediv__(self, other: float) -> Self:
        return Point(np.divide(self.p, other))

    def __matmul__(self, tf: Transform) -> Self:
        return Point(self.p @ tf.m)

    def length(self) -> float:
        return self.dist(Point())

    def dist(self, other: Point) -> float:
        return sqrt(self.dist2(other))

    def dist2(self, other: Point) -> float:
        return np.sum(np.square(np.delete((self - other).p, [3])))

    def x(self) -> float:
        return self.p[0]

    def y(self) -> float:
        return self.p[1]

    def z(self) -> float:
        return self.p[2]

    def replace_x(self, xx: float) -> Point:
        result = self.copy()
        result.p[0] = xx
        return result

    def replace_y(self, yy: float) -> Point:
        result = self.copy()
        result.p[1] = yy
        return result

    def replace_z(self, zz: float) -> Point:
        result = self.copy()
        result.p[2] = zz
        return result

#
# Transform class - a matrix representing a 3D transformation consisting of
# a 3D rotation followed by a translation
#   

class Transform:

    def __init__(self, other: type[None|np.ndarray]=None, **kwargs: float):
        self.m: np.ndarray
        if other is None:
            self.m = np.identity(4)
        else:
            self.m = other
        for name, v in kwargs.items():
            match name:
                case 'x':
                    self.m[3][0] = v
                case 'y':
                    self.m[3][1] = v
                case 'z':
                    self.m[3][2] = v
                case 'xrot':
                    self._copy_rotate(self @ Transform.xrot(v))
                case 'yrot':
                    self._copy_rotate(self @ Transform.yrot(v))
                case 'zrot':
                    self._copy_rotate(self @ Transform.zrot(v))
                case _:
                    raise NameError(f"unknown keyword arg '{name}' to Transform()")
            

    def copy(self) -> Transform:
        return Transform(self.m.copy())

    def _copy_rotate(self, other: Transform) -> None:
        for i in range(3):
            for j in range(3):
                self.m[i][j] = other.m[i][j]

    def __matmul__(self, other: Self) -> Self:
        return Transform(self.m @ other.m)

    def __str__(self) -> str:
        return str(self.clean().m)

    def clean(self) -> Self:
        return Transform(np.round(self.m, 3))

    def __neg__(self) -> Self:
        return Transform(linalg.inv(self.m))

    def __mul__(self, other: Transform|float) -> Self:
        return Transform(self.m * other)

    def __truediv__(self, other: Transform|float) -> Self:
        return Transform(self.m / other)

#
# between - approximate interpolation (only suitable for small angles)
#

    def between(self, other: Transform, where: float) -> Transform:
        return Transform(self.m * (1-where) + other.m * where)

#
# xlate - add translation (replacing existing translation)
#

    def xlate(self, p: Point) -> Self:
        result = self.copy()
        result.m[3][0] = p.x()
        result.m[3][1] = p.y()
        result.m[3][2] = p.z()
        return result

#
# add_xlate - modify existing translation
#
        
    def add_xlate(self, p: Point) -> Self:
        result = self.copy()
        result.m[3][0] += p.x()
        result.m[3][1] += p.y()
        result.m[3][2] += p.z()
        return result
#
# replace_... - replace a single dimension of the translation
#

    def replace_x(self, xx: float) -> Transform:
        result = self.copy()
        result.m[3][0] = xx
        return result

    def replace_y(self, yy: float) -> Transform:
        result = self.copy()
        result.m[3][1] = yy
        return result

    def replace_z(self, zz: float) -> Transform:
        result = self.copy()
        result.m[3][2] = zz
        return result
#
# get whole translation
#
    def get_xlate(self) -> Point:
        return Point(self.x(), self.y(), self.z())
#
# extract individual dimensions of the translation
#
    def x(self) -> float:
        return self.m[3][0]

    def y(self) -> float:
        return self.m[3][1]

    def z(self) -> float:
        return self.m[3][2]

#
# xrot/yrot/zrot - create rotation in the corresponding axis
#

    @staticmethod
    def xrot(angle: float) :
        c = dcos(angle)
        s = dsin(angle)
        return Transform(np.array([[1, 0, 0, 0], [0 , c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]]))

    @staticmethod
    def yrot(angle: float) :
        c = dcos(angle)
        s = dsin(angle)
        return Transform(np.array([[c, 0, s, 0], [0 , 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]]))
        
    @staticmethod
    def zrot(angle: float) :
        c = dcos(angle)
        s = dsin(angle)
        return Transform(np.array([[c, -s, 0, 0], [s , c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]))

class Line:
    def __init__(self, p0: Point, p1: Point):
        self.p0, self.p1 = p0, p1

    def length(self) -> float:
        return p0.dist(p1)

    def along(self, where: float) -> Point:
        return (self.p1 - self.p0) * where + self.p0

    def bisect(self) -> Point:
        return self.along(0.5)
        

    

