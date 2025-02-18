#coding:utf-8

from __future__ import annotations
from body import *
from params import *
from leg import *
from logger import Logger

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

    def set_posture(self, posture: Transform) -> None:
        self.posture = posture
        self.body.set_body_height(self.posture.z())

    def set_named_posture(self, pname: str) -> None:
        self.body.set_named_posture(pname)

    def walk(self, distance: float, direction: float, speed:float = 0.0) -> None:
        stride = Transform().xlate(Point(self.step_size/2, 0, 0)) @ (Transform.zrot(direction))
        Logger.info(f'control.walk distance {distance}')
        step_count = int(distance / self.step_size)
        for s in range(step_count):
            self.body.step(stride, self.step_height)
        for s in range(self.body.get_step_count()):
            self.body.step(Transform(), self.step_height)

