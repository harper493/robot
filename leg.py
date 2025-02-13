from __future__ import annotations
from geometry import *
import numpy as np
from typing import Self
from dtrig import *
from math import *
from dataclasses import dataclass

@dataclass
class LegAngles:
    cox_angle: float = 0.0
    femur_angle: float = 0.0
    tibia_angle: float = 0.0

class Leg:

    def __init__(self, _number: int, _position: Point, _femur: float, _tibia: float):
        self.number, self.position, self.femur, self.tibia = _number, _position, _femur, _tibia

    def get_femur_tibia(self, toe_pos: Point2D) -> LegAngles:
        result = LegAngles()
        h = toe_pos.length()
        alpha = toe_pos.angle()
        beta = cosine_rule(h, self.femur, self.tibia)
        result.femur_angle = beta - alpha
        result.tibia_angle = cosine_rule(self.tibia, self.femur, h)
        return result

    def get_toe_pos_2D(self, angles: LegAngles) -> Point2D:
        knee_pos = Point2D.from_polar(self.femur, angles.femur_angle).reflect_y()
        alpha = angles.tibia_angle - (90 - angles.femur_angle)
        toe_offset = Point2D.from_polar(self.tibia, 90 - alpha)
        return (knee_pos + toe_offset).reflect_x()

class QuadLeg(Leg):

    def __init__(self, _number: int, _position: Point, _femur: float, _tibia: float):
        super(QuadLeg, self).__init__(_number, _position, _femur, _tibia)

    def get_angles(self, toe_pos: Point) -> LegAngles:
        cox = datan2(toe_pos.y(), -toe_pos.z())
        result = self.get_femur_tibia(Point2D(toe_pos.x(), -toe_pos.z() * dcos(cox)))
        result.cox_angle = cox
        return result

    def get_toe_pos(self, angles: LegAngles) -> Point:
        t1 = self.get_toe_pos_2D(angles)
        print(t1)
        h = t1.y()
        return Point(t1.x(), h * dsin(angles.cox_angle), h * dcos(angles.cox_angle)) 

