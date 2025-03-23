#coding:utf-8

from __future__ import annotations
import numpy as np
import scipy    #type: ignore[import-untyped,import]
from numpy import linalg
from dtrig import *
from math import *
from dataclasses import dataclass
from logger import Logger

SMALL = 1e-9

#
# Useful stand-alone functions
#

def hypot(x: float, y: float) -> float:    #type: ignore[no-redef]
    return sqrt(x*x + y*y)

def hypot2(x: float, y: float) -> float:
    return x*x + y*y

def sign(x: float) -> float :
    return -1 if x<0 else 1

def dist(x0: float, y0: float, x1: float, y1: float) -> float:    #type: ignore[no-redef]
    return sqrt(dist2(x0, y0, x1, y1))

def dist2(x0: float, y0: float, x1: float, y1: float) -> float:
    dx = x1-x0
    dy = y1-y0
    return dx*dx + dy*dy

def cosine_rule(l1: float, l2: float, opposite: float) -> float:
    try:
        result = dacos((l1*l1 + l2*l2 - opposite*opposite) / (2*l1*l2))
    except (ValueError, ZeroDivisionError):
        Logger.error(f'cosine rule error {l1} {l2} {opposite}')
        result = 90
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

    def clean(self) -> Point2D:
        return Point2D(np.round(self.p, 3))
        
    def __str__(self) -> str:
        c = self.clean()
        return f'(x={c.x():.3f} y={c.y():.3f})'

    def __add__(self, other) -> Point2D:
        if isinstance(other, Point2D):
            return Point2D(np.add(self.p, other.p))
        else:
            return Point2D(np.add(self.p, other))

    def __sub__(self, other) -> Point2D:
        if isinstance(other, Point2D):
            return Point2D(np.subtract(self.p, other.p))
        else:
            return Point2D(np.subtract(self.p, other))

    def __mul__(self, x: float) -> Point2D:
        return Point2D(np.multiply(self.p, x))

    def __truediv__(self, x: float) -> Point2D:
        return Point2D(np.divide(self.p, x))

    def __eq__(self, other: Point2D) -> bool:    #type: ignore
        return equal(self.x(), other.x()) and equal(self.y(), other.y())

    def __ne__(self, other: Point2D) -> bool:    #type: ignore
        return not (self==other)

    def x(self) -> float:
        return self.p[0]

    def y(self) -> float:
        return self.p[1]

    def length(self) -> float:
        return hypot(self.x(), self.y())

    def angle(self) -> float:
        return datan2(self.x(), self.y())

    def reflect_x(self) -> Point2D:
        return Point2D(self.x(), -self.y())

    def reflect_y(self) -> Point2D:
        return Point2D(-self.x(), self.y())

    def dist(self, other: Point2D) -> float:
        return sqrt(self.dist2(other))

    def dist2(self, other: Point2D) -> float:
        return np.sum(np.square((self - other).p))

    @staticmethod
    def from_polar(r: float, theta: float) -> Point2D:
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

    def copy(self) -> Point:
        return Point(self.p.copy())

    def clean(self) -> Point:
        return Point(np.round(self.p, 3))
        
    def __str__(self) -> str:
        c = self.clean()
        return f'(x={c.x():.3f} y={c.y():.3f} z={c.z():.3f})'

    def __neg__(self) -> Point:
        return Point((-self.p))

    def __add__(self, other) -> Point:
        if isinstance(other, Point):
            return Point(np.add(self.p, other.p))
        else:
            return Point(np.add(self.p, other))
        
    def __sub__(self, other) -> Point:
        if isinstance(other, Point):
            return Point(np.subtract(self.p, other.p))
        else:
            return Point(np.subtract(self.p, other))

    def __eq__(self, other: Point) -> bool:    #type: ignore
        return (equal(self.x(), other.x())
                and equal(self.y(), other.y())
                and equal(self.z(), other.z()))

    def __ne__(self, other: Point) -> bool:    #type: ignore
        return not (self==other)
    
    def __mul__(self, other: float) -> Point:
        return Point(np.multiply(self.p, other))
    
    def __truediv__(self, other: float) -> Point:
        return Point(np.divide(self.p, other))

    def __matmul__(self, tf: Transform) -> Point:
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

    def xrot(self) -> float:
        return datan2(-self.z(), self.y())

    def yrot(self) -> float:
        return datan2(self.z(), self.x())

    def zrot(self) -> float:
        return datan2(-self.y(), self.x())

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

    def reflect_x(self) -> Point:
        result = self.copy()
        result.p[0] = -result.p[0]
        return result

    def reflect_y(self) -> Point:
        result = self.copy()
        result.p[1] = -result.p[1]
        return result

    def reflect_z(self) -> Point:
        result = self.copy()
        result.p[2] = -result.p[1]
        return result

#
# Angles: represent the three roll/pitch/yaw angles
#

@dataclass
class Angles:

    pitch: float = 0.0
    roll: float = 0.0
    yaw: float = 0.0

    def __add__(self, other: float|Angles) -> Angles:
        if isinstance(other,float):
            return Angles(self.roll + other, self.pitch + other, self.yaw + other)
        else:
            return Angles(self.roll + other.roll, self.pitch + other.pitch, self.yaw + other.yaw)

    def __neg__(self) -> Angles:
        return Angles(-self.roll, - self.pitch, -self.yaw)

    def __sub__(self, other: float|Angles) -> Angles:
        return self + (-other)

    def __mul__(self, mult: float) -> Angles:
        return Angles(self.roll * mult, self.pitch * mult, self.yaw * mult)
        
    def __truediv__(self, div: float) -> Angles:
        return Angles(self.roll / div, self.pitch / div, self.yaw / div)
    
    def __eq__(self, other: Angles) -> bool:
        return self.roll == other.roll and self.pitch == other.pitch and self.yaw == other.yaw

    def __ne__(self, other: Angles) -> bool:
        return not self == other

    def __str__(self) -> str:
        return f'roll: {self.roll:.1f} pitch: {self.pitch:.1f} yaw: {self.yaw:.1f}'

#
# Transform class - a matrix representing a 3D transformation consisting of
# a 3D rotation followed by a translation
#   

class Transform:

    def __init__(self, other: None|Point|np.ndarray=None, **kwargs: float):
        self.m: np.ndarray
        if other is None:
            self.m = np.identity(4)
        elif isinstance(other, Point):
            self.m = np.array([[1, 0, 0, 0],
                               [0, 1, 0, 0],
                               [0, 0, 1, 0],
                               [other.x(), other.y(), other.z(), 1]])
        elif isinstance(other, np.ndarray):
            self.m = other
        else:
            raise TypeError(f'incorrect type {type(other)} in Transform.init')
        if kwargs:
            xlate = Point()
            for name, v in kwargs.items():
                match name:
                    case 'x':
                        xlate = xlate.replace_x(v)
                    case 'y':
                        xlate = xlate.replace_y(v)
                    case 'z':
                        xlate = xlate.replace_z(v)
                    case 'xrot':
                        self._copy_rotate(self @ Transform.make_xrot(v))
                    case 'yrot':
                        self._copy_rotate(self @ Transform.make_yrot(v))
                    case 'zrot':
                        self._copy_rotate(self @ Transform.make_zrot(v))
                    case _:
                        raise NameError(f"unknown keyword arg '{name}' to Transform()")
            self.update_xlate(xlate)
            


    def copy(self) -> Transform:
        return Transform(self.m.copy())

    def _copy_rotate(self, other: Transform) -> None:
        for i in range(3):
            for j in range(3):
                self.m[i][j] = other.m[i][j]

    def __matmul__(self, other: Transform) -> Transform:
        return Transform(self.m @ other.m)

    def __str__(self) -> str:
        return str(self.clean().m)

    def clean(self) -> Transform:
        return Transform(np.round(self.m, 3))

    def __neg__(self) -> Transform:
        return Transform(linalg.inv(self.m))

    def __mul__(self, other: Transform|float) -> Transform:
        return Transform(self.m * other)

    def __truediv__(self, other: Transform|float) -> Transform:
        return Transform(self.m / other)

#
# between - approximate interpolation (only suitable for small angles)
#

    def between(self, other: Transform, where: float) -> Transform:
        return Transform(self.m * (1-where) + other.m * where)

#
# xlate - add translation (replacing existing translation)
#

    def xlate(self, p: Point) -> Transform:
        result = self.copy()
        result.m[3][0] = p.x()
        result.m[3][1] = p.y()
        result.m[3][2] = p.z()
        return result

#
# add_xlate - modify existing translation
#
        
    def add_xlate(self, p: Point) -> Transform:
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
# reflect_... - reflect in the other two planes
#
    def reflect_x(self) -> Transform:
        result = self.copy()
        result.m[3][0] = -result.m[3][0]
        return result

    def reflect_y(self) -> Transform:
        result = self.copy()
        result.m[3][1] = -result.m[3][1]
        return result

    def reflect_z(self) -> Transform:
        result = self.copy()
        result.m[3][2] = -result.m[3][2]
        return result
#
# in-situ update of translation
#
    def update_xlate(self, p: Point) -> Transform:
        self.m[3][0] = p.x()
        self.m[3][1] = p.y()
        self.m[3][2] = p.z()
        return self
#
# square root
#
    def sqrt(self) -> Transform:
        return Transform(scipy.linalg.sqrtm(self.m))

    def power(self, pow: float) -> Transform:
        return Transform(scipy.linalg.expm(scipy.linalg.logm(self.m) / pow))
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
# xrot/yrot/zrot - get effectve rotation in each of the three axes
#

    def xrot(self) -> float:
        return (Point(0, 1, 0) @ self).xrot()

    def yrot(self) -> float:
        return (Point(1, 0, 0) @ self).yrot()

    def zrot(self) -> float:
        return (Point(1, 0, 0) @ self).zrot()

#
# make_xrot/yrot/zrot - create rotation in the corresponding axis
#

    @staticmethod
    def make_xrot(angle: float) -> Transform:
        c = dcos(angle)
        s = dsin(angle)
        return Transform(np.array([[1, 0, 0, 0], [0 , c, -s, 0], [0, s, c, 0], [0, 0, 0, 1]]))

    @staticmethod
    def make_yrot(angle: float) -> Transform:
        c = dcos(angle)
        s = dsin(angle)
        return Transform(np.array([[c, 0, s, 0], [0 , 1, 0, 0], [-s, 0, c, 0], [0, 0, 0, 1]]))
        
    @staticmethod
    def make_zrot(angle: float) -> Transform:
        c = dcos(angle)
        s = dsin(angle)
        return Transform(np.array([[c, -s, 0, 0], [s , c, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]))
#
# create from a string in the order x y z xrot yrot zrot
#
    @staticmethod
    def from_string(config: str) -> Transform:
        if '=' in config:
            try:
                d = { cc.split('=', 1)[0] : float(cc.split('=', 1)[1]) for cc in config.split() }
                return Transform(**d)    #type: ignore[arg-type]
            except:
                data = []
        else:
            try:
                data = [ float(v) for v in config.split() ]
                if len(data) ==  3:
                    data += [0, 0, 0]
                elif len(data) != 6:
                    data = []
            except ValueError:
                data = []
        if data:
            return Transform(x=data[0], y=data[1], z=data[2],
                             xrot=data[3], yrot=data[4], zrot=data[5])
        else:
            raise ValueError(f"invalid transform specification '{config}'")
            

class Line:
    def __init__(self, p0: Point, p1: Point):
        self.p0, self.p1 = p0, p1

    def length(self) -> float:
        return self.p0.dist(self.p1)

    def along(self, where: float) -> Point:
        return (self.p1 - self.p0) * where + self.p0

    def bisect(self) -> Point:
        return self.along(0.5)
        

    

