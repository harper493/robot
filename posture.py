#coding:utf-8

from __future__ import annotations
from geometry import *

class Posture:

    def __init__(self, name: str, config: str):
        self.name = name
        self.values: dict[str, Point] = {}
        self.parse(config)

    def __str__(self) -> str:
        return ', '.join([ f'{n} : {str(p)[1:-1]}' for n, p in self.values.items() ])

    def get(self, lname: str) -> Point:
        try:
            return self.values[lname]
        except KeyError:
            try:
                return self.values['all']
            except KeyError:
                return Point()

    def parse(self, text: str) -> None:
        for leg_str in text.split(','):
            leg_split = leg_str.split(':', 1)
            if len(leg_split) > 1:
                lname, tfm_str = leg_split[0].strip(), leg_split[1]
            else:
                lname, tfm_str = 'all', leg_str
            self.values[lname] = Transform.from_string(tfm_str).reflect_z().get_xlate()
