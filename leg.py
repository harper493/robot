#coding:utf-8

from __future__ import annotations
from geometry import *
import numpy as np
from typing import Self
from dtrig import *
from math import *
from dataclasses import dataclass
from enum import Enum
from params import Params
from servo_action import ServoAction

@dataclass
class LegAngles:
    cox_angle: float = 0.0
    femur_angle: float = 0.0
    tibia_angle: float = 0.0

@dataclass
class ServoIds:
    cox_servo: int
    femur_servo: int
    tibia_servo: int

class StepPhase(Enum):
    clear = 1
    lift = 2
    drop = 3
    pose = 4
    
class Leg:

    def __init__(self, _number: int, _location: Point, _femur: float, _tibia: float,
                 _servo_ids: ServoIds):
        self.number, self.location, self.femur, self.tibia = _number, _location, _femur, _tibia
        self.servo_ids = _servo_ids
        self.position = Point()
        self.start = Point()
        self.clear_height = Params.get("clear_height")

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

    def goto(self, target: Point) -> tuple[ServoAction]:
        angles = self.get_angles(target)
        self.position = target
        result = (
            ServoAction(self.servo_ids.cox_servo, angles.cox_angle),
            ServoAction(self.servo_ids.femur_servo, angles.femur_angle),
            ServoAction(self.servo_ids.tibia_servo, angles.tibia_angle))
        return result

    def step(self, phase: StepPhase, target: Point, height: float=0.0) -> tuple[ServoAction]:
        match phase:
            case StepPhase.clear:
                self.start = self.position
                return self.goto(self.start.replace_z(self.position.z() + self.clear_height))
            case StepPhase.lift:
                p1 = (Line(self.start, target)
                      .bisect()
                      .replace_z(self.start.z() + (height or Params.get("step_height"))))
                return self.goto(p1)
            case StepPhase.drop:
                self.start = self.position
                return self.goto(target.replace_z(target.z() + self.clear_height))
            case StepPhase.pose:
                return self.goto(target)

class QuadLeg(Leg):

    def __init__(self, _number: int, _position: Point, _femur: float, _tibia: float,
                 _servo_ids: ServoIds):
        super(QuadLeg, self).__init__(_number, _position, _femur, _tibia, _servo_ids)

    def get_angles(self, toe_pos: Point) -> LegAngles:
        cox = datan2(toe_pos.y(), -toe_pos.z())
        result = self.get_femur_tibia(Point2D(toe_pos.x(), -toe_pos.z() / dcos(cox)))
        result.cox_angle = cox + 90
        return result

    def get_toe_pos(self, angles: LegAngles) -> Point:
        t1 = self.get_toe_pos_2D(angles)
        h = t1.y()
        return Point(t1.x(), -h * dsin(angles.cox_angle - 90), h * dcos(angles.cox_angle - 90)) 

