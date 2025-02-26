#coding:utf-8

from __future__ import annotations
from body import *
from params import *
from leg import *
from servo import *
from logger import Logger
import re

class Control:

    def __init__(self, b: Body):
        self.body = b
        self.position = Point2D()
        self.height: float = Params.get('default_height')
        self.posture = Transform()
        self.step_size: float = Params.get('default_step_size')
        self.step_height: float = Params.get('default_step_height')
        self.default_gait = None
        Logger.init()

    def set_height(self, height: float) -> None:
        self.body.set_body_height(height)

    def set_posture(self, pname: str) -> None:
        self.body.set_named_posture(pname)

    def set_servo(self, pos: str, value: str) -> None:
        m1 = re.match(r'(?:(?:([fr\*])([lr\*]?)([cft]))|(h))', pos)
        m2 = re.match(r'([+-]?)(\d+)', value)
        if m1 and m2:
            fr, lr, joint, head = m1.groups()
            diff, angle = m2.groups()
            if fr=='*' and not lr:
                lr = '*'
            if head is None:
                sname = (fr+ lr + joint)
            else:
                sname = 'h'
            for s in self.body.get_servos(sname):
                servo = Servo.get(s)
                if diff:
                    delta = float(diff + angle)
                    servo.adjust_angle(delta)
                else:
                    servo.set_angle(float(angle))
        elif m1 is None:
            raise ValueError(f"invalid servo identifier '{pos}'")
        else:
            raise ValueError(f"invalid servo position '{value}'")

