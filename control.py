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
        self.step_height = Params.get('default_step_height')
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

