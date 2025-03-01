#coding:utf-8

from __future__ import annotations
from params import *
from typing import Any

class Globals:

    speed: float

    @staticmethod
    def init():
        Globals.speed = Params.get('default_speed')

    @staticmethod
    def set(name: str, value: Any) -> None:
        setattr(Globals, name, value)
