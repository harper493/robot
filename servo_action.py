#coding:utf-8

from dataclasses import dataclass
from collections import OrderedDict
from logger import  Logger
import time

@dataclass
class ServoAction:
    channel: int
    angle: float

class ServoActionList:

    def __init__(self, _max_iter: int=10, _speed: int=300):
        self.max_iter, self.speed = _max_iter, _speed
        self.actions = OrderedDict()
        self.positions = {}
        #self.my_servo = Servo()

    def __str__(self) -> str:
        return '\n'.join([ f'{ch}: {round(a,1)}' for ch,a in self.actions.items() ])

    def __len__(self) -> int:
        return len(self.actions)

    def append(self, chan: int, angle: float) -> None:
        self.actions[chan] = angle

    def exec(self) -> None:
        Logger.info(f'ServoAction actions {str(self)}')
        deltas = { chan:(angle - self.get_position(chan)) for chan,angle in self.actions.items() }
        max_delta = max([ abs(d) for d in deltas.values() ])
        iterations = int((max_delta + self.max_iter - 1) // self.max_iter)
        Logger.info(f'ServoActon deltas:{deltas} max delta {max_delta} iterations {iterations}')
        for i in range(iterations):
            for chan,d in deltas.items():
                if i+1 == iterations:
                    pos = self.actions[chan]
                else:
                    pos = self.get_position(chan) + (d / iterations)
                #self.my_servo.setServoAngle(chan, pos)
                self.positions[chan] = pos
                time.sleep(1.0 / self.speed)
        self.actions = {}

    def get_position(self, chan: int) -> float:
        p = self.positions.get(chan, None)
        if p is None:
            p = 90
            self.positions[chan] = p
        return p

        
