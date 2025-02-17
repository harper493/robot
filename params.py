#coding:utf-8

from __future__ import annotations
import json
from typing import Iterator
from copy import copy

defaults = {
    "clear_height" : 0.3,
    "default_step_height" : 0.5,
    "default_height" : 2.5,
    "femur_length" : 2,
    "tibia_length" : 2.3,
    "default_step_size" : 1,
    "leg_fl_servo_cox" : 4,
    "leg_fl_servo_femur" : 3,
    "leg_fl_servo_tibia" : 2,
    "leg_fr_servo_cox" : 11,
    "leg_fr_servo_femur" : 12,
    "leg_fr_servo_tibia" : 13,
    "leg_rl_servo_cox" : 7,
    "leg_rl_servo_femur" : 6,
    "leg_rl_servo_tibia" : 5,
    "leg_rr_servo_cox" : 8,
    "leg_rr_servo_femur" : 9,
    "leg_rr_servo_tibia" : 10,
    "leg_fl_x" : 85,
    "leg_fl_y" : 50,
    "leg_fl_z" : 0,
    "leg_fr_x" : 85,
    "leg_fr_y" : -50,
    "leg_fr_z" : 0,
    "leg_rl_x" : -90,
    "leg_rl_y" : 50,
    "leg_rl_z" : 0,
    "leg_rr_x" : -90,
    "leg_rr_y" : -50,
    "leg_rr_z" : 0,
    "gait_default" : "fl,rr,fr,rl"
    }

class ParamGroup:

    def __init__(self, _filename: str):
        self.filename = _filename
        try:
            with open(self.filename) as f:
                self.values = { name:self._parse_value(value) for name,value in json.loads(f.read()).items() }
        except:
            self.values = copy(defaults)
            self.save()

    def get(self, pname: str) -> float:
        result = self.values.get(pname)
        if result is None:
            raise ValueError(f"unknown parameter '{pname}'")
        return float(result)

    def get_or(self, pname: str, dflt: float) -> float:
        result = self.values.get(pname)
        if result is None:
            result = dflt
        return float(result)
    
    def get_str(self, pname: str) -> str:
        result = self.values.get(pname)
        if result is None:
            raise ValueError(f"unknown parameter '{pname}'")
        return str(result)

    def exists(self, pname: str) -> bool:
        return str in self.values

    def enumerate(self) -> Iterator[tuple[str, str|float]]:
        for i in self.values.items():
            yield i

    def update(self, name: str, value: float) -> None:
        self.values[name] = value
        self.save()

    def save(self) -> None:
        with open(self.filename, 'w') as f:
            f.write(json.dumps(self.values))
            f.write('\n')

    def __iter__(self):
        for i in self.values.items():
            yield i

    def _parse_value(sel, value):
        try:
            return float(value)
        except ValueError:
            return value

class Params:
    
    @staticmethod
    def get(pname: str) -> float:
        return the_params.get(pname)

    @staticmethod
    def get_or(pname: str, dflt: float) -> float:
        return the_params.get_or(pname, dflt)        
    
    @staticmethod
    def get_str(pname: str) -> str:
        return the_params.get_str(pname)

    @staticmethod
    def exists(pname: str) -> bool:
        return the_params.exists(pname)

    @staticmethod
    def enumerate() -> Iterator[tuple[str, str|float]]:
        for i in the_params.values.items():
            yield i
    
the_params = ParamGroup('parameters.txt')
