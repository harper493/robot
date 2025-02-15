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

class Body:

    def __init__(self, height: float=0.0):
        self.position = Point()
        self.attitude = Transform()
        self.absolute_position = Point()
        self.legs: dict[str, Leg] = {}
        self.gaits = OrderedDict()
        self.cur_gait: list[tuple[str]] | None = None
        self.step_iter = iter(itertools.cycle(self.gaits.items()))
        self.transform = Transform().replace_z(height or Params.get('default_height'))

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
        self.step_iter = iter(itertools.cycle(self.gaits[gname]))
        self.step_iter = iter(itertools.cycle(self.gaits[gname]))

    def step(self, stride: Transform) -> None:
        lift_legs = next(self.step_iter)
        other_legs = [ ll for ll in self.legs.values() if ll not in lift_legs ]
        unstride = (-stride).replace_z(stride.z())
        Logger.info(f'starting step at {self.position} \nstride {stride.get_xlate()} \nunstride {unstride.get_xlate()}')
        actions = ServoActionList()
        for ll in lift_legs:
            ll.start_step(stride)
        for ll in other_legs:
            ll.start_step(unstride)
        for ll in lift_legs:
            ll.step(StepPhase.clear, actions)
        actions.exec()
        for ll in lift_legs:
            ll.step(StepPhase.lift, actions)
        for ll in other_legs:
            ll.step(StepPhase.advance_1, actions)
        actions.exec()
        for ll in lift_legs:
            ll.step(StepPhase.drop, actions)
        for ll in other_legs:
            ll.step(StepPhase.advance_2, actions)
        actions.exec()
        for ll in lift_legs:
            ll.step(StepPhase.pose, actions)
        actions.exec()
        Logger.info(f'body position {self.position}')
        for ll in self.legs.values():
            Logger.info(f'leg {ll.which} toe position {ll.end_step()}')
        self.position = self.position @ stride
                
            
                    
