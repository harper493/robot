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
    advance_1 = 5
    advance_2 = 6
    
class Leg:

    def __init__(self, _number: int, _which: str, _location: Point, _femur: float, _tibia: float,
                 _servo_ids: ServoIds):
        self.number, self.location, self.which = _number, _location, _which
        self.femur, self.tibia = _femur, _tibia
        self.servo_ids = _servo_ids
        self.position = Point()
        self.start = Point()
        self.angles = LegAngles()
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

    def goto(self, target: Point, actions: ServoActionList) -> None:
        angles = self.get_angles(target)
        self.angles = angles
        actions.append(self.servo_ids.cox_servo, angles.cox_angle)
        actions.append(self.servo_ids.femur_servo, angles.femur_angle)
        actions.append(self.servo_ids.tibia_servo, angles.tibia_angle)

    def start_step(self, stride: Transform) -> None:
        self.start = self.position
        self.stride = (self.position @ stride) - self.position
        self.half_stride = stride / 2
        self.dest = self.position + self.stride

    def step(self, phase: StepPhase, actions: ServoActionList) -> None:
        match phase:
            case StepPhase.clear:
                self.goto(self.start.replace_z(self.position.z() + self.clear_height), actions)
            case StepPhase.lift:
                p1 = (Line(self.start, self.dest)
                      .bisect()
                      .replace_z(self.start.z() + (Params.get("step_height"))))
                self.goto(p1, actions)
            case StepPhase.drop:
                self.goto((self.dest).replace_z(self.dest.z() + self.clear_height), actions)
            case StepPhase.pose:
                self.goto(self.dest, actions)
            case StepPhase.advance_1:
                self.goto(self.start @ self.half_stride, actions)
            case StepPhase.advance_2:
                self.goto(self.dest, actions)

    def end_step(self) -> Position:
        return self.get_toe_pos(self.angles)

class QuadLeg(Leg):

    def __init__(self, _number: int, _which: str, _position: Point, _femur: float, _tibia: float,
                 _servo_ids: ServoIds):
        super(QuadLeg, self).__init__(_number, _which, _position, _femur, _tibia, _servo_ids)

    def get_angles(self, toe_pos: Point) -> LegAngles:
        cox = datan2(toe_pos.y(), -toe_pos.z())
        result = self.get_femur_tibia(Point2D(toe_pos.x(), -toe_pos.z() / dcos(cox)))
        result.cox_angle = cox + 90
        return result

    def get_toe_pos(self, angles: LegAngles) -> Point:
        t1 = self.get_toe_pos_2D(angles)
        h = t1.y()
        return Point(t1.x(), -h * dsin(angles.cox_angle - 90), h * dcos(angles.cox_angle - 90)) 

