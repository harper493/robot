#coding:utf-8

from __future__ import annotations
from geometry import *
import numpy as np
from typing import Self, Type, Iterable
from dtrig import *
from math import *
from dataclasses import dataclass
from enum import Enum
from params import Params
from servo_action import *
from servo import *
from logger import Logger

class Head:

    head_positions = {
        'default' : 90,
        'ahead' : 90,
        'up' : 45,
        'highest' : 0,
        'down' : 135,
        'lowest' : 180,
        }

    def __init__(self, servos: Iterable[int]):
        self.servos = [ s for s in servos ]
        for n, s in enumerate(self.servos):
            Servo.enroll(f'head_{n}', s, False)
        self.position = 91.0

    def goto(self, angle: float, actions: ServoActionList) -> None:
        self.position = angle

    def get_position(self) -> float:
        return self.position

    def goto_named(self, where: str, actions: ServoActionList) -> None:
        try:
            angle = Head.head_positions[where]
        except KeyError:
            raise ValueError(f"unknown head position '{where}'")
        self.goto(angle, actions)

    @staticmethod
    def make_head(_type: str, servos: Iterable[int]) -> Head:
        try:
            _type = type_list[_type]
        except KeyError:
            raise ValueError("unknown head type '{_type}'")
        result = _type(servos)
        return result

class SimpleHead(Head):

    def __init__(self, servos: Iterable[int]):
        super(SimpleHead, self).__init__(servos)

    def goto(self, angle: float, actions: ServoActionList) -> None:
        self.position = angle
        actions.append(self.servos[0], angle)

type_list = {
    'none' : Head,
    'simple' : SimpleHead,
    }
        
        
    
