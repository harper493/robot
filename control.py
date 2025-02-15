#coding:utf-8

from __future__ import annotations
from body import *
from params import *
from leg import *
from logger import Logger

class Control:

    def __init__(self, _body: Body):
        self.body = _body
        self.position = Point2D()
        self.height = Params.get('default_height')
        self.posture = Transform()
        self.step_size = Params.get('default_step_size')
        Logger.init()

    def walk(self, distance: float, direction: float, speed:float = 0.0) -> None:
        stride = Transform().xlate(Point(self.step_size, 0, 0)) @ (Transform.zrot(direction))
        step_count = int(distance / self.step_size)
        for s in range(step_size):
            body.step(stride)

    def build_quad(self):
        for w in ('fl','fr', 'rl', 'rr'):
            self.body.add_leg(QuadLeg, w)
