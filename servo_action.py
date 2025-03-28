#coding:utf-8

from __future__ import annotations
from typing import Self, Type, Iterable
from dataclasses import dataclass
from collections import OrderedDict
from logger import  Logger
from servo import Servo
from params import Params
from globals import Globals
import time

@dataclass
class ServoAction:
    channel: int
    angle: float

class ServoActionList:

    def __init__(self, speed = 0.0):
        self.max_iter = Params.get('max_servo_iteration')
        self.speed = speed or Globals.speed
        self.actions: dict[int,float] = OrderedDict()    #type: ignore[annotation-unchecked]

    def __str__(self) -> str:
        return ', '.join([ f'{ch}: {round(a,1)}' for ch,a in self.actions.items() ])

    def __enter__(self) -> Self:
        return self

    def __exit__(self, _type, value, traceback) -> None:
        if _type is None:
            self.exec()

    def __len__(self) -> int:
        return len(self.actions)

    def append(self, chan: int, angle: float) -> None:
        self.actions[chan] = angle

    def exec(self) -> None:
        #Logger.info(f'ServoAction actions {str(self)}')
        deltas = { chan:(angle - Servo.get(chan).get_position())
                   for chan,angle in self.actions.items() }
        max_delta = max([ abs(d) for d in deltas.values() ])
        iterations = int((max_delta + self.max_iter - 1) // self.max_iter)
        delta_str = ', '.join([ f'{ch}: {round(a,1)}' for ch,a in deltas.items() ])
        #Logger.info(f'ServoActon deltas:{delta_str} max delta {max_delta:.1f} iterations {iterations}')
        for i in range(iterations):
            for chan,d in deltas.items():
                s = Servo.get(chan)
                if i+1 == iterations:
                    pos = self.actions[chan]
                else:
                    pos = s.get_position() + (d / iterations)
                s.set_angle(pos)
                if self.speed:
                    time.sleep(1.0 / (self.speed * 80))
        self.actions = {}

        
