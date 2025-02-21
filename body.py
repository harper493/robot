#coding:utf-8

from __future__ import annotations
from geometry import *
import numpy as np
from typing import Self, Type
from dtrig import *
from math import *
from dataclasses import dataclass
from enum import Enum
from params import Params
from servo_action import *
from leg import *
from posture import Posture
from gait import Gait
import itertools
from logger import Logger
from collections import OrderedDict

class Body:

    def __init__(self, height: float=0.0):
        self.position = Point()
        self.attitude = Transform()
        self.absolute_position = Point()
        self.legs: dict[str, Leg] = {}
        self.head_servo = 0
        self.gaits: dict[str, Gait] = Params.make_dict('gait', Gait)
        self.postures: dict[str, Posture] = Params.make_dict('posture', Posture)
        self.default_gait = self.gaits.get('default', next(iter(self.gaits.values())))
        self.cur_gait = self.default_gait
        self.step_iter = iter(self.cur_gait)
        self.height: float = Params.get('default_height')
        self.prev_stride = 0.0

    def add_leg(self, leg_type: Type, which: str) -> None:
        prefix = f'leg_{which}_'
        pos = Point(Params.get(prefix+'x'),
                    Params.get(prefix+'y'),
                    Params.get(prefix+'z'))
        servos = ServoIds(int(Params.get(prefix+'servo_cox')),
                          int(Params.get(prefix+'servo_femur')),
                          int(Params.get(prefix+'servo_tibia')))
        femur = Params.get_or(prefix+'femur', Params.get('femur_length'))
        tibia = Params.get_or(prefix+'tibia', Params.get('tibia_length'))
        self.legs[which] = leg_type(len(self.legs), which, pos, femur, tibia, servos)

    def set_gait(self, gname: str) -> None:
        self.cur_gait = self.gaits[gname]
        self.step_iter = iter(self.cur_gait)    #type: ignore[assignment]

    def set_named_posture(self, pname: str) -> None:
        try:
            self.posture = self.postures[pname]
        except KeyError:
            raise ValueError(f"unknown posture '{pname}'")
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

    def set_leg_position(self, name: str, x: float, y: float, z:float) -> None:
        ll = self.get_leg(name)
        actions = ServoActionList()
        ll.goto(Point(x, y, z), actions)
        actions.exec()
        
    def get_step_count(self) -> int:
        return self.cur_gait.get_step_count()

    def get_servos(self, name: str) -> list[int]:
        if name=='h':
            return [ self.head_servo ]
        elif len(name) >= 3:
            return [ ll.get_servo(name[2])
                     for ll in self.legs.values()
                     if (name[0]=='*' or name[0]==ll.which[0])
                         and (name[1]=='*' or name[1]==ll.which[1])]
        else:
            return []

    def get_leg(self, name: str) -> Leg:
        try:
            return self.legs[name]
        except KeyError:
            raise ValueError(f"unknown leg '{name}'")
    
    def step(self, stride_tfm: Transform, height: float) -> None:
        from command import CommandInterpreter
        stride = stride_tfm.get_xlate()
        lift_legs = [ self.legs[ll] for ll in next(self.step_iter) ]    #type: ignore[call-overload]
        other_legs = [ ll for ll in self.legs.values() if ll not in lift_legs ]
        unstride = (-stride).replace_z(stride.z()) / (self.get_step_count() - 1)
        dest = stride / 2
        Logger.info(f'starting step at {self.position}')
        Logger.info(f'...stride {stride} unstride {unstride}')
        actions = ServoActionList()
        for ll in lift_legs:
            ll.start_step(dest + ll.rest_position, height)
        for ll in lift_legs:
            ll.step(StepPhase.clear, actions)
        actions.exec()
        CommandInterpreter.the_command.pause()
        for ll in lift_legs:
            ll.step(StepPhase.lift, actions)
        for ll in other_legs:
            ll.move_by(unstride, actions)
        actions.exec()
        CommandInterpreter.the_command.pause()
        for ll in lift_legs:
            ll.step(StepPhase.drop, actions)
        for ll in other_legs:
            ll.move_by(unstride, actions)
        actions.exec()
        CommandInterpreter.the_command.pause()
        for ll in lift_legs:
            ll.step(StepPhase.pose, actions)
        actions.exec()
        CommandInterpreter.the_command.pause()
        self.position = self.position + stride
        Logger.info(f'body position {self.position}')
        for ll in self.legs.values():
            ll.end_step()
            Logger.info(f'leg {ll.which} toe position {ll.position}')

    def pause(self) -> None:
        from command import CommandInterpreter
        ci = CommandInterpreter.the_command
        ci.pause()

    def build_quad(self):
        for w in ('fl','fr', 'rl', 'rr'):
            self.add_leg(QuadLeg, w)
        actions = ServoActionList()
        for ll in self.legs.values():
            ll.goto(Point(ll.tibia, 0, -ll.femur), actions)
        actions.exec()

    def show_position(self) -> str:
        return str(self.position)

    def show_legs(self) -> str:
        return '\n'.join([ ll.show_position() for ll in self.legs.values() ])

    @staticmethod
    def make_body(_type: str) -> Body:
        try:
            fn = type_list[_type]
        except KeyError:
            raise ValueError("unknown body type '{_type}'")
        result = Body()
        fn(result)
        return result
                
type_list = {
    'quad' : Body.build_quad,
    }

            
                    
