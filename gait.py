#coding:utf-8

from __future__ import annotations
import itertools

class Gait:

    def __init__(self, name: str, config: str):
        self.name = name
        self.order = [ tuple([ ll for ll in ss.split('+') ]) for ss in config.split(',') ]

    def __str__(self) -> str:
        return ','.join([ '+'.join([ ll for ll in ss]) for ss in self.order])

    def __iter__(self):
        return itertools.cycle(self.order)

    def get_step_count(self) -> int:
        return len(self.order)
