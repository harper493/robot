#coding:utf-8

import json
from copy import copy

defaults = {
    "clear_height" : 0.3,
    "step_height" : 0.7
    }

class Params:

    the_params = None

    def __init__(self, _filename: str):
        self.filename = _filename
        try:
            with open(self.filename) as f:
                self.values = { name:float(value) for name,value in json.loads(f.read().items()) }
        except:
            self.values = copy(defaults)
            self.save()
        Params.the_params = self

    def get(self, pname: str):
        return self.values.get(pname, None)

    def update(self, name: str, value: float):
        self.values[name] = value
        self.save()

    def save(self):
        with open(self.filename, 'w') as f:
            f.write(json.dumps(self.values))
            f.write('\n')

    @staticmethod
    def get(pname: str):
        return Params.the_params.values.get(pname)
    
Params('parameters.txt')
