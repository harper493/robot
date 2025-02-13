from __future__ import annotations
import numpy as np
import scipy
from numpy import linalg
from typing import Self
from dtrig import *
from math import *

SMALL = 1e-9

class Point:

    def __init__(self, x=None, y: float=0.0, z: float=0.0):
        if isinstance(x, np.ndarray):
            self.p = x
            self.p[3] = 1
        else:
            self.p = np.array([x or 0.0, y, z, 1])

    def copy(self) -> Self:
        return Point(self.p.copy())

    def clean(self) -> Self:
        return Point(np.round(self.p, 3))
        
    def __str__(self) -> str:
        c = self#.clean()
        return f'({c.x():.3f} {c.y():.3f} {c.z():.3f})'

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


class Transform:

    def __init__(self, other: type[None|np.ndarray]=None):
        if other is None:
            self.m = np.identity(4)
        else:
            self.m = other

    def copy(self) -> Transform:
        return Transform(self.m.copy())

    def __matmul__(self, other: Self) -> Self:
        return Transform(self.m @ other.m)

    def __str__(self) -> str:
        return str(self.clean().m)

    def clean(self) -> Self:
        return Transform(np.round(self.m, 3))

    def __neg__(self) -> Self:
        return Transform(linalg.inv(self.m))

    def xlate(self, p: Point) -> Self:
        result = self.copy()
        result.m[0][3] = p.x()
        result.m[1][3] = p.y()
        result.m[2][3] = p.z()
        return result
        
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
    def __init__(self, p0, p1):
        self.p0, self.p1 = p0, p1

    def length(self) -> float:
        return p0.dist(p1)

