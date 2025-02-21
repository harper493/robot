#coding:utf-8

from __future__ import annotations
from geometry import *
import numpy as np
from typing import Self, Iterator
from dtrig import *
from math import *
from dataclasses import dataclass
from enum import Enum
from params import Params
from servo_action import *
from logger import Logger

@dataclass
class LegAngles:
    cox: float = 0.0
    femur: float = 0.0
    tibia: float = 0.0

    def __neg__(self) -> LegAngles:
        return LegAngles(cox=-self.cox,
                         femur=-self.femur,
                         tibia=-self.tibia)

    def __str__(self) -> str:
        return f'cox {round(self.cox, 1)} femur {round(self.femur, 1)} tibia {round(self.tibia, 1)}'

@dataclass
class ServoIds:
    cox: int
    femur: int
    tibia: int

    def __iter__(self) -> Iterator[tuple[str,int]]:
        yield ('cox', self.cox)
        yield ('femur', self.femur)
        yield ('tibia', self.tibia)

class StepPhase(Enum):
    clear = 1
    lift = 2
    drop = 3
    pose = 4
    
class Leg:

    def __init__(self, _number: int, _which: str, _location: Point, _femur: float, _tibia: float,
                 _servo_ids: ServoIds, _rest_position: Point = Point()):
        self.number, self.location, self.which = _number, _location, _which
        self.femur, self.tibia = _femur, _tibia
        self.servo_ids = _servo_ids
        rev = (self.which[1]=='r')
        self.servos = { ch : Servo.enroll((self.which + name[0]), ch, ((not rev) ^ (name=='cox')))
                        for name,ch in self.servo_ids }
        self.position = Point()
        self.start = Point()
        self.angles = LegAngles()
        self.clear_height: float = Params.get("clear_height")
        self.rest_position = _rest_position

    def set_rest_position(self, pos: Point) -> None:
        self.rest_position = pos

    def get_femur_tibia(self, toe_pos: Point2D) -> LegAngles:
        result = LegAngles()
        h = toe_pos.length()
        if h > self.tibia + self.femur:
            raise ValueError(f'leg.get_femur_tibia: impossible position {toe_pos}')
        alpha = toe_pos.angle()
        beta = cosine_rule(h, self.femur, self.tibia)
        result.femur = 90 - (beta - alpha)
        result.tibia = cosine_rule(self.tibia, self.femur, h)
        #print(f'femur_tibia pos {toe_pos} {h=} {alpha=} {beta=} angles {result}')
        return result

    def get_toe_pos_2D(self, angles: LegAngles) -> Point2D:
        knee_pos = Point2D.from_polar(self.femur, angles.femur).reflect_y()
        alpha = angles.tibia - (90 - angles.femur)
        toe_offset = Point2D.from_polar(self.tibia, 90 - alpha)
        return (knee_pos + toe_offset).reflect_x()

    def goto(self, target: Point, actions: ServoActionList) -> None:
        try:
            self.angles = self.get_angles(target)
        except ValueError as exc:
            Logger.error(f"leg '{self.which}' target{target} ({exc})")
            raise exc
        Logger.info(f"goto leg '{self.which}' target{target} angles {self.angles}")
        actions.append(self.servo_ids.cox, self.angles.cox)
        actions.append(self.servo_ids.femur, self.angles.femur)
        actions.append(self.servo_ids.tibia, self.angles.tibia)
        self.position = target

    def start_step(self, dest: Point, height: float) -> None:
        self.start = self.position
        self.height = height
        self.dest = dest

    def step(self, phase: StepPhase, actions: ServoActionList) -> None:
        match phase:
            case StepPhase.clear:
                self.goto(self.start.replace_z(self.start.z() + self.clear_height), actions)
            case StepPhase.lift:
                p1 = (Line(self.start, self.dest)
                      .bisect()
                      .replace_z(self.start.z() + self.height))
                Logger.info(f'lift leg {self.which} p1 {p1} start {self.start} dest {self.dest}')
                self.goto(p1, actions)
            case StepPhase.drop:
                self.goto((self.dest).replace_z(self.dest.z() + self.clear_height), actions)
            case StepPhase.pose:
                self.goto(self.dest, actions)

    def end_step(self) -> Point:
        self.position = self.get_toe_pos(self.angles)
        return self.position

    def move_by(self, delta: Point, actions: ServoActionList) -> None:
        Logger.info(f"move_by leg '{self.which}' start {self.position} delta {delta}")
        self.goto(self.position + delta, actions)

    def get_angles(self, toe_pos: Point) -> LegAngles:    # always overridden
        return LegAngles()

    def get_toe_pos(self, angles: LegAngles) -> Point:    # always overridden
        return Point()

    def get_servo(self, which: str) -> int:
        match which:
            case 'c':
                return self.servo_ids.cox
            case 'f':
                return self.servo_ids.femur
            case 't':
                return self.servo_ids.tibia
            case _:
                return -1

    def show_position(self) -> str:
        return f"Leg '{self.which}' position {str(self.position)[1:-1]} angles {self.angles}"
 
class QuadLeg(Leg):

    def __init__(self, _number: int, _which: str, _position: Point, _femur: float, _tibia: float,
                 _servo_ids: ServoIds):
        super(QuadLeg, self).__init__(_number, _which, _position, _femur, _tibia, _servo_ids)

    def get_angles(self, toe_pos: Point) -> LegAngles:
        cox = datan2(toe_pos.y(), -toe_pos.z())
        try:
            result = self.get_femur_tibia(Point2D(toe_pos.x(), -toe_pos.z() / dcos(cox)))
        except ValueError as exc:
            raise exc
        result.cox = cox + 90
        return result

    def get_toe_pos(self, angles: LegAngles) -> Point:
        t1 = self.get_toe_pos_2D(angles)
        h = t1.y()
        return Point(t1.x(), -h * dsin(angles.cox - 90), h * dcos(angles.cox - 90)) 

