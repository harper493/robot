#coding:utf-8

from __future__ import annotations
import json
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

class Params:

    def __init__(self, _filename: str):
        self.filename = _filename
        try:
            with open(self.filename) as f:
                self.values = { name:self._parse_value(value) for name,value in json.loads(f.read()).items() }
        except:
            self.values = copy(defaults)
            self.save()

    def get2(self, pname: str, miss_ok: bool=False) -> float|str|None:
        result = self.values.get(pname, None)
        if result is None and not miss_ok:
            raise ValueError(f"unknown parameter '{pname}'")
        return result

    def update(self, name: str, value: float) -> None:
        self.values[name] = value
        self.save()

    def save(self) -> None:
        with open(self.filename, 'w') as f:
            f.write(json.dumps(self.values))
            f.write('\n')

    def __iter__(self):
        for i in self.items():
            yield i

    def _parse_value(sel, value):
        try:
            return float(value)
        except ValueError:
            return value


    @staticmethod
    def get(pname: str) -> float:
        result = the_params.values.get(pname)
        if result is None:
            raise ValueError(f"unknown parameter '{pname}'")
        return float(result)

    @staticmethod
    def get_or(pname: str, dflt: float) -> float:
        result = the_params.values.get(pname)
        if result is None:
            result = dflt
        return float(result)

    
    @staticmethod
    def get_str(pname: str) -> str:
        result = the_params.values.get(pname)
        if result is None:
            raise ValueError(f"unknown parameter '{pname}'")
        return str(result)

    @staticmethod
    def exists(pname: str) -> bool:
        return str in the_params.values

    @staticmethod
    def enumerate():
        for i in the_params.values.items():
            yield i
    
the_params = Params('parameters.txt')
