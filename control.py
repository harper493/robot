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
        self.default_gait = None
        Logger.init()

    def walk(self, distance: float, direction: float, speed:float = 0.0) -> None:
        stride = Transform().xlate(Point(self.step_size, 0, -self.height)) @ (Transform.zrot(direction))
        print(self.height, stride)
        step_count = int(distance / self.step_size)
        for s in range(step_count):
            self.body.step(stride)

    def build_quad(self):
        for w in ('fl','fr', 'rl', 'rr'):
            self.body.add_leg(QuadLeg, w)
        for p,v in Params.enumerate():
            if p.startswith('gait_'):
                gname = p.split('_')[1]
                self.body.add_gait(gname, v)
                if self.default_gait is None or gname=='default':
                    self.body.set_gait(gname)
                    self.default_gait = gname
        actions = ServoActionList()
        for ll in self.body.legs.values():
            ll.goto(Point(ll.tibia, 0, -ll.femur), actions)
        actions.exec()

