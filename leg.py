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

#
# The Leg class (and subclasses) represents a single robot leg. It knows how
# to do forward and reverse kinematics, and how to work its associated
# servos.
#
# The start_step and step functions coordinate actions around a single
# step, i.e. one or more legs mpove forard (i.e. in the desired direction
# of travel) while the others slowly advance the body. The walk function
# performs multple steps as necessary to achieve the desired trajectory.
#
# There is one ugly complication. Leg popsitions are expressed symmetrically.
# In particular, the y axis is always positive for movement inwards, towards
# the center. But... when computing trajectories, we need to use the absolute
# position relative to the ground. The functions get_global_position
# and from_global_position make the corresponding adjustments. It's ery
# important to remember which variety to use.
#

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
        self.reverse = (self.which[1]=='r')
        self.servos = { ch : Servo.enroll((self.which + name[0]), ch, ((not self.reverse) ^ (name=='cox')))
                        for name,ch in self.servo_ids }
        self.position = Point()
        self.start = Point()
        self.angles = LegAngles()
        self.clear_height: float = Params.get("clear_height")
        self.step_height: float = Params.get("default_step_height")
        self.rest_position = _rest_position

    def __str__(self) -> str:
        return f'{self.which} {self.position}'

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
        knee_pos = Point2D(-self.femur * dcos(angles.femur), self.femur * dsin(angles.femur))
        alpha = angles.tibia - angles.femur
        toe_offset = Point2D(self.tibia * dcos(alpha), self.tibia * dsin(alpha))
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

    def start_step(self, step: Point, step_height: float) -> None:
        self.start = self.position
        self.step_height = step_height
        self.this_step = step
        self.dest = self.start + step
        Logger.info(f'leg.start_step \'{self.which}\' start {self.start} step {step} dest {self.dest}')

    def step(self, phase: StepPhase, actions: ServoActionList) -> None:
        match phase:
            case StepPhase.clear:
                self.goto(self.start.replace_z(self.start.z() + self.clear_height), actions)
            case StepPhase.lift:
                p1 = (self.start + self.this_step / 2).replace_z(-self.step_height)
                #Logger.info(f'lift leg {self.which} p1 {p1} start {self.start} dest {self.dest}')
                self.goto(p1, actions)
            case StepPhase.drop:
                self.goto((self.dest).replace_z(self.dest.z() + self.clear_height), actions)
            case StepPhase.pose:
                self.goto(self.dest, actions)

    def end_step(self) -> Point:
        self.position = self.get_toe_pos(self.angles)
        return self.position

    def move_by(self, delta: Point, actions: ServoActionList) -> None:
        #Logger.info(f"move_by leg '{self.which}' start {self.position} delta {delta}")
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

    def get_dist_from_rest(self) -> float:
        return self.position.dist(self.rest_position)
            
    def get_global_position(self)-> Point:
        return self.position.reflect_y() if self.reverse else self.position

    def from_global_position(self, p: Point) -> Point:
        return p.reflect_y() if self.reverse else p

    def get_global_rest_position(self) -> Point:
        return self.from_global_position(self.rest_position)

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

