#coding:utf-8

from __future__ import annotations
from params import *


class Globals:

    speed: float

    @staticmethod
    def init():
        Globals.speed = Params.get('default_speed')
