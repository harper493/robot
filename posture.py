#coding:utf-8

from __future__ import annotations
from geometry import *

class Posture:

    def __init__(self, config: str):
        self.transform = Transform.from_string(config)
        print(config, self.transform)

    def __str__(self) -> str:
        return str(self.transform)

    def get(self) -> Transform:
        return self.transform

    def get_xlate(self) -> Point:
        return self.transform.get_xlate()
