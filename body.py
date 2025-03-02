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
from robot_keyword import *
from collections import OrderedDict

type_list: dict[str,Type] = { }    #type: ignore[no-redef]

class Body:

    attitude_keywords = KeywordTable(
        ('backward', 'b',''),
        ('forward', 'f', ''),
        ('height', 'h', ''),
        ('left', 'l', ''),
        ('normal', 'n', ''),
        ('pitch', 'p', ''),
        ('right', 'r', ''),
        ('roll', 'ro', ''),
        ('yaw', 'y', ''),
        )

    def __init__(self):
        self.position = Point()
        self.prev_attitude = self.attitude = Transform()
        self.absolute_position = Point()
        self.legs: dict[str, Leg] = {}
        self.head_servo = 0
        self.gaits: dict[str, Gait] = Params.make_dict('gait', Gait)
        self.postures: dict[str, Posture] = Params.make_dict('posture', Posture)
        self.posture = self.postures['relax']
        self.default_gait = self.gaits.get('default', next(iter(self.gaits.values())))
        self.cur_gait = self.default_gait
        self.step_iter = iter(self.cur_gait)
        self.height: float = Params.get('default_height')
        self.step_size: float = Params.get('default_step_size')
        self.step_height: float = Params.get('default_step_height')
        self.spread = 0.0
        self.stretch = 0.0
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

    def set_height(self, height: float) -> None:
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

    def set_attitude(self, which: str, value: float) -> None:
        self.prev_attitude = self.attitude
        key = Body.attitude_keywords.find(which)
        match key.name[0]:
            case 'b':
                self.attitude = self.attitude.replace_x(-value)
            case 'f':
                self.attitude = self.attitude.replace_x(value)
            case 'h':
                self.attitude = self.attitude.replace_z(value)
            case 'l':
                self.attitude = self.attitude.replace_y(-value)
            case 'n':
                self.attitude = Transform()
            case 'p':
                self.attitude = self.attitude @ Transform(yrot=value)
            case 'r':
                if key.name=='right': 
                    self.attitude = self.attitude.replace_y(value)
                else:
                    self.attitude = self.attitude @ Transform(xrot=value)
            case 'y':
                self.attitude = self.attitude @ Transform(zrot=value)
        self.reposition_body()
            
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

    def set_servos(self, name: str, value: str) -> None:
        v = float(value)
        for s in self.get_servos(name):
            servo = Servo.get(s)
            if value[0]=='+' or value[0]=='-':
                servo.adjust_angle(v)
            else:
                servo.set_angle(v)

    def set_stretch(self, s: float) -> None:
        self.stretch = s
        self.reposition_feet()

    def set_spread(self, s: float) -> None:
        self.spread = s
        self.reposition_feet()

    def get_leg(self, name: str) -> Leg:
        try:
            return self.legs[name]
        except KeyError:
            raise ValueError(f"unknown leg '{name}'")

    def set_head_pos(self, angle: float, actions: ServoActionList) -> None:
        self.head.goto(angle, actions)
    
    def one_step(self, step: Point,
                 unstride: Point,
                 lift_legs: Iterable[Leg],
                 other_legs: Iterable[Leg]) -> None:
        from command import CommandInterpreter
        with ServoActionList() as actions:
            for ll in lift_legs:
                ll.start_step(step, -self.height + self.step_height)
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
        self.position = self.position - unstride * 2
        #Logger.info(f'body.one_step final position {self.position}')

    def walk(self, distance: float, dir: float, turn: float, speed:float = 0.0) -> None:
        straight = (dir < 20) or (dir > 340) or (dir > 160 and dir < 200)
        step_size = min(distance,
                        self.step_size if straight else min(self.step_size, Params.get('small_step_size')))
        stride = Transform(Point(step_size, 0, 0) @ Transform(zrot=dir))
        step_count = int(distance / step_size)
        Logger.info(f'body.walk {distance=} {dir=} {step_size=} stride {stride.get_xlate()} {step_count=}')
        for s in range(step_count):
            lift_legs = [ self.legs[ll] for ll in next(self.step_iter) ]    #type: ignore[call-overload]
            other_legs = [ ll for ll in self.legs.values() if ll not in lift_legs ]
            unstride = (-stride).replace_z(stride.z()).get_xlate() / ((self.cur_gait.get_step_count() - 1) * 2)
            for ll in lift_legs:
                s1 = (ll.get_global_position() + (ll.location @ self.attitude)) @ stride
                step = ll.from_global_position(s1 - ((ll.location @ self.attitude) + ll.get_global_position()))
                self.one_step(step, unstride, lift_legs, other_legs)
        Logger.info(f'body.walk end position {self.position} legs:\n{self.show_legs()}')
        ll0 = lift_legs[0]
        total_unstride = ll.from_global_position(ll0.position - ll0.rest_position)
        one_unstride = total_unstride / len(other_legs)
        remaining_unstride = total_unstride
        for ll in sorted(other_legs, key=Leg.get_dist_from_rest, reverse=True):
            remaining_unstride -= one_unstride
            target = ll.get_global_rest_position() + remaining_unstride
            step = ll.from_global_position(target - ll.get_global_position())
            others = [ lll for lll in self.legs.values() if lll is not ll ]
            Logger.info(f"body '{ll.which}' rem unstr {remaining_unstride} target {target} step {step}")
            self.one_step(step, -one_unstride / 2, [ll], others)
        Logger.info(f'body.walk final position {self.position} legs:\n{self.show_legs()}')

    def reposition_body(self) -> None:
        with ServoActionList() as actions:
            for ll in self.legs.values():
                new_loc = ll.location @ -self.attitude
                old_loc = ll.location @ -self.prev_attitude
                loc_adjust =  new_loc - old_loc 
                new_pos = ll.from_global_position(loc_adjust) + ll.position
                print(f'{ll.which} {old_loc} {new_loc} {ll.position} {loc_adjust} {new_pos}')
                ll.goto(new_pos, actions)

    def reposition_feet(self) -> None:
        for ll in self.legs.values():
            base_pos = self.posture.get(ll.which)
            x_delta = (self.stretch/2 if ll.which[0]=='f'
                       else -self.stretch/2 if ll.which[0]=='r'
                       else 0)
            new_pos = Point(base_pos.x() + x_delta, base_pos.y() - self.spread/2, -self.height)
            #print(f'{base_pos} {self.spread=} {self.stretch=} {new_pos}')
            if new_pos != ll.position:
                self.one_step(new_pos - ll.position, Point(), [ll], [])

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

    def show_attitude(self) -> str:
        if self.attitude.x() >= 0:
            xstr = 'forward'
            xval = self.attitude.x()
        else:
            xstr = 'backward'
            xval = -self.attitude.x()
        if self.attitude.y() >= 0:
            ystr = 'right'
            yval = self.attitude.y()
        else:
            ystr = 'left'
            yval = -self.attitude.y()
        angles = self.attitude.xlate(Point(0, 0, 0))
        return (f"Base posture: '{self.posture.name}' stretch {self.stretch:.2f} spread {self.spread:.2f}" +
                f"\nAttitude: {xstr} {xval:.1f} {ystr} {yval:.1f} height {self.attitude.z():.1f}" +
                f" yaw {angles.zrot():.1f} pitch {angles.yrot():.1f} roll {angles.xrot():.1f}")

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
