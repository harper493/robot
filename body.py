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
from servo_action import *
from leg import *
import itertools
from logger import Logger
from collections import OrderedDict

named_postures = {
    'stand' : Transform(x=1.0, z=-2.5)
    }

class Body:

    def __init__(self, height: float=0.0):
        self.position = Point()
        self.attitude = Transform()
        self.absolute_position = Point()
        self.legs: dict[str, Leg] = {}
        self.gaits = OrderedDict()
        self.cur_gait: list[tuple[str]] | None = None
        self.step_iter = None
        self.height = Params.get('default_height')
        self.prev_stride = 0.0

    def add_leg(self, type: Leg, which: str) -> None:
        prefix = f'leg_{which}_'
        pos = Point(Params.get(prefix+'x'),
                    Params.get(prefix+'y'),
                    Params.get(prefix+'z'))
        servos = ServoIds(int(Params.get(prefix+'servo_cox')),
                          int(Params.get(prefix+'servo_femur')),
                          int(Params.get(prefix+'servo_tibia')))
        femur = Params.get(prefix+'femur', True) or Params.get('femur_length')
        tibia = Params.get(prefix+'tibia', True) or Params.get('tibia_length')
        self.legs[which] = type(len(self.legs), which, pos, femur, tibia, servos)

    def add_gait(self, gname: str, descr: str) -> None:
        gait = []
        for d in descr.split(','):
            gait.append(tuple([ self.legs[dd] for dd in d.split('+') ]))
        self.gaits[gname] = gait
        Logger.info(f'adding gait \'{gname}\': {descr}')

    def set_gait(self, gname: str) -> None:
        self.cur_gait = self.gaits[gname]
        self.step_iter = iter(itertools.cycle(self.cur_gait))

    def set_named_posture(self, pname: str) -> None:
        self.posture = named_postures[pname]
        actions = ServoActionList()
        for ll in self.legs.values():
            pos = self.posture.get_xlate()
            ll.set_rest_position(pos)
            ll.goto(pos, actions)
        actions.exec()

    def set_body_height(self, height: float) -> None:
        if height != self.height:
            actions = ServoActionList()
            delta = Point(0, 0, -(height - self.height))
            for ll in self.legs.values():
                ll.move_by(delta, actions)
            actions.exec()
            self.height = height
            
    def get_step_count(self) -> int:
        return len(self.cur_gait)

    def step(self, stride_tfm: Transform, height: float) -> None:
        stride = stride_tfm.get_xlate()
        lift_legs = next(self.step_iter)
        other_legs = [ ll for ll in self.legs.values() if ll not in lift_legs ]
        unstride = (-stride).replace_z(stride.z()) / (self.get_step_count() - 1)
        dest = stride / 2
        Logger.info(f'starting step at {self.position}')
        Logger.info(f'stride {stride} unstride {unstride}')
        actions = ServoActionList()
        for ll in lift_legs:
            ll.start_step(dest + ll.rest_position, height)
        for ll in lift_legs:
            ll.step(StepPhase.clear, actions)
        actions.exec()
        for ll in lift_legs:
            ll.step(StepPhase.lift, actions)
        for ll in other_legs:
            ll.move_by(unstride, actions)
        actions.exec()
        for ll in lift_legs:
            ll.step(StepPhase.drop, actions)
        for ll in other_legs:
            ll.move_by(unstride, actions)
        actions.exec()
        for ll in lift_legs:
            ll.step(StepPhase.pose, actions)
        actions.exec()
        self.position = self.position + stride
        Logger.info(f'body position {self.position}')
        for ll in self.legs.values():
            ll.end_step()
            Logger.info(f'leg {ll.which} toe position {ll.position}')
                
            
                    
