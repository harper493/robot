#coding:utf-8

from __future__ import annotations
import json
from typing import Iterator
from copy import copy

class ParamGroup:

    def __init__(self, _filename: str, defaults: dict[str, str]):
        if _filename:
            self.filename = _filename
            try:
                with open(self.filename) as f:
                    self.values = { name:self._parse_value(value) for name,value in json.loads(f.read()).items() }
            except FileNotFoundError:
                self.values = copy(defaults)
            for p,v in defaults.items():
                if p not in self.values:
                    self.values[p] = self._parse_value(v)
            self.save()

    def get(self, pname: str) -> float:
        result = self.values.get(pname)
        if result is None:
            raise ValueError(f"unknown parameter '{pname}'")
        return float(result)

    def get_or(self, pname: str, dflt: float) -> float:
        result = self.values.get(pname)
        if result is None:
            result = dflt
        return float(result)
    
    def get_str(self, pname: str) -> str:
        result = self.values.get(pname)
        if result is None:
            raise ValueError(f"unknown parameter '{pname}'")
        return str(result)

    def exists(self, pname: str) -> bool:
        return str in self.values

    def enumerate(self) -> Iterator[tuple[str, str|float]]:
        for i in self.values.items():
            yield i

    def update(self, name: str, value: float) -> None:
        self.values[name] = value
        self.save()

    def save(self) -> None:
        with open(self.filename, 'w') as f:
            f.write(json.dumps(self.values))
            f.write('\n')

    def __iter__(self):
        for i in self.values.items():
            yield i

    def _parse_value(sel, value):
        try:
            return float(value)
        except ValueError:
            return value

the_params = ParamGroup('', {})

class Params:
    
    @staticmethod
    def get(pname: str) -> float:
        return the_params.get(pname)

    @staticmethod
    def get_or(pname: str, dflt: float) -> float:
        return the_params.get_or(pname, dflt)        
    
    @staticmethod
    def get_str(pname: str) -> str:
        return the_params.get_str(pname)

    @staticmethod
    def exists(pname: str) -> bool:
        return the_params.exists(pname)

    @staticmethod
    def enumerate() -> Iterator[tuple[str, str|float]]:
        for i in the_params.values.items():
            yield i

    @staticmethod
    def load(filename: str, defaults: dict[str, str]) -> None:
        global the_params
        the_params = ParamGroup(filename, defaults)
