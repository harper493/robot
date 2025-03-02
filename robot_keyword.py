#coding:utf-8

from __future__ import annotations
from dataclasses import dataclass
from typing import Iterable

@dataclass
class Keyword:
    name: str
    abbrev: str
    help: str

class KeywordTable:

    def __init__(self, *keywords: Iterable[str]):
        self.keywords = [ Keyword(*k) for k in keywords ]

    def find(self, word: str, miss_ok: bool=False) -> Keyword:
        for k in self.keywords:
            if k.name.startswith(word) and word.startswith(k.abbrev):
                return k
        else:
            if miss_ok:
                return Keyword('', '', '')
            else:
                raise ValueError(f"unknown or ambiguous keyword '{word}'")

    def __iter__(self):
        for k in self.keywords:
            yield k
        
    def help(self) -> str:
        return '\n'.join([ f'{k.name:10} {k.help}' for k in self.keywords ])


