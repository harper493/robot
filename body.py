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
from head import *
from posture import Posture
from gait import Gait
import itertools
from logger import Logger
from collections import OrderedDict

type_list: dict[str,Type] = { }    #type: ignore[no-redef]

class Body:

    def __init__(self):
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
        self.step_size: float = Params.get('default_step_size')
        self.step_height: float = Params.get('default_step_height')
        self.spread = 0.0
        self.stretch = 0.0
        self.prev_stride = 0.0
        self.build()

    def add_leg_base(self, leg_type: Type, which: str) -> Leg:
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
        return self.legs[which]

    def set_gait(self, gname: str) -> None:
        self.cur_gait = self.gaits[gname]
        self.step_iter = iter(self.cur_gait)    #type: ignore[assignment]

    def set_named_posture(self, pname: str) -> None:
        try:
            self.posture = self.postures[pname]
        except KeyError:
            raise ValueError(f"unknown posture '{pname}'")
        with ServoActionList() as actions:
            for ll in self.legs.values():
                pos = self.posture.get(ll.which)
                ll.set_rest_position(pos)
                ll.goto(pos, actions)

    def set_body_height(self, height: float) -> None:
        if height != self.height:
            with ServoActionList() as actions:
                delta = Point(0, 0, -(height - self.height))
                for ll in self.legs.values():
                    ll.move_by(delta, actions)
            self.height = height

    def set_leg_position(self, name: str, x: float, y: float, z:float) -> None:
        ll = self.get_leg(name)
        with ServoActionList() as actions:
            ll.goto(Point(x, y, z), actions)
        
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

    def set_head_pos(self, angle: float, actions: ServoActionList) -> None:
        self.head.goto(angle, actions)
    
    def step(self, stride: Transform, height: float) -> None:
        from command import CommandInterpreter
        Logger.info(f'body.step stride\n{stride}')
        lift_legs = [ self.legs[ll] for ll in next(self.step_iter) ]    #type: ignore[call-overload]
        other_legs = [ ll for ll in self.legs.values() if ll not in lift_legs ]
        unstride = (-stride).replace_z(stride.z()).get_xlate() / ((self.get_step_count() - 1) * 2)
        half_stride = stride.sqrt()
        Logger.info(f'starting step at {self.position}')
        Logger.info(f'...stride\n{stride}\nunstride {unstride}')
        with ServoActionList() as actions:
            for ll in lift_legs:
                s1 = (ll.get_global_position() + ll.location) @ stride
                step = ll.from_global_position(s1 - (ll.location + ll.get_global_position()))
                Logger.info(f'lift {ll.which} pos {ll.position} loc {ll.location} s1 {s1} s2 {ll.location @ stride} step {step}')
                ll.start_step(step, height)
            for ll in lift_legs:
                ll.step(StepPhase.clear, actions)
        CommandInterpreter.the_command.pause()
        with ServoActionList() as actions:
            for ll in lift_legs:
                ll.step(StepPhase.lift, actions)
            for ll in other_legs:
                ll.move_by(ll.from_global_position(unstride), actions)
        CommandInterpreter.the_command.pause()
        with ServoActionList() as actions:
            for ll in lift_legs:
                ll.step(StepPhase.drop, actions)
            for ll in other_legs:
                ll.move_by(ll.from_global_position(unstride), actions)
        CommandInterpreter.the_command.pause()
        with ServoActionList() as actions:
            for ll in lift_legs:
                ll.step(StepPhase.pose, actions)
        CommandInterpreter.the_command.pause()
        self.position = self.position + (stride.get_xlate())
        Logger.info(f'body position {self.position}')
        for ll in self.legs.values():
            ll.end_step()
            Logger.info(f'leg {ll.which} toe position {ll.position} global {ll.get_global_position()}')

    def walk(self, distance: float, dir: float, turn: float, speed:float = 0.0) -> None:
        straight = (dir < 20) or (dir > 340) or (dir > 160 and dir < 200)
        step_size = self.step_size if straight else \
            min(self.step_size, Params.get('small_step_size'))
        stride = Transform(Point(step_size, 0, 0) @ Transform(zrot=dir))
        Logger.info(f'control.walk distance {distance} stride\n{stride}')
        step_count = int(distance / step_size)
        for s in range(step_count):
            self.step(stride, self.step_height)
        for s in range(self.get_step_count()):
            self.step(Transform(), self.step_height)            

    def pause(self) -> None:
        from command import CommandInterpreter
        ci = CommandInterpreter.the_command
        ci.pause()

    def build(self) -> None:
        self.build_base()

    def build_base(self) -> None:
        self.head = Head.make_head(Params.get_str('head_type'), [ int(Params.get('head_servo')) ])

    def show_position(self) -> str:
        return f"{str(self.position)} Head angle: {self.head.get_position()}"

    def show_legs(self) -> str:
        return '\n'.join([ ll.show_position() for ll in self.legs.values() ])

    @staticmethod
    def make_body(_type: str) -> Body:
        try:
            c = type_list[_type]
        except KeyError:
            raise ValueError("unknown body type '{_type}'")
        result = c()
        return result

class QuadBody(Body):

    def __init__(self):
        super(QuadBody, self).__init__()

    def build(self) -> None:
        for w in ('fl','fr', 'rl', 'rr'):
            self.add_leg(w)
        self.build_base()

    def add_leg(self, which: str) -> Leg:
        return self.add_leg_base(QuadLeg, which)
                
type_list = {
    'none' : Body,
    'quad' : QuadBody,
    }

            
                    
