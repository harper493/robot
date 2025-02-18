#!/usr/bin/python
#coding:utf-8

from __future__ import annotations
from control import *
from body import *
from params import *
from leg import *
from logger import Logger
from command import CommandInterpreter
try:
    import readline
except ImportError :
    readline = None     #type: ignore[assignment]

def run(control: Control) -> None:
    interpreter = CommandInterpreter(control)
    while True:
        print('robot> ', end='')
        try:
            cmd = input()
        except:
            print('\n')
            break
        if cmd:
            try:                     
                interpreter.execute(cmd)
            except StopIteration:
                break
            except ValueError as exc:
                print("Error:", str(exc.args[0]))

def init() -> Control:
    Params.load('parameters.txt')
    Logger.init('log.txt')
    body = Body.make_body(Params.get_str('body_type'))
    return Control(body)

if __name__ == '__main__':
    run(init())

