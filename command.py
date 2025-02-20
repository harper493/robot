#coding:utf-8

from __future__ import annotations
import time
import re
import json
from control import Control
from dataclasses import dataclass
from collections.abc import Callable
from logger import Logger
from servo import Servo
from params import Params
from platform import Platform

@dataclass
class CommandInfo:
    name: str
    abbrev: str
    help: str

class CommandInterpreter:

    the_command: CommandInterpreter = None    #type: ignore[assign]

    the_commands = (
        CommandInfo('height', 'he', 'set height'),
        CommandInfo('help', 'h', 'get help'),
        CommandInfo('leg', 'l', 'set leg position explicitly: leg leg-name x y z'),
        CommandInfo('posture', 'p', 'set static posture'),
        CommandInfo('quit', 'q', 'terminate program'),
        CommandInfo('save', 'sav', 'save current position as calibration'),
        CommandInfo('servo', 'ser', 'modify servo position explicitly'),
        CommandInfo('set', 'set', 'modify parameter'),
        CommandInfo('show', 'sh', 'show something'),
        CommandInfo('turn', 't', 'walk while turning: turn distance angle [direction]'),
        CommandInfo('verbose', 'v', 'set verbosity level'),        
        CommandInfo('walk', 'w', 'walk in straight line: walk distance [direction]'),
        )

    show_commands = (
        CommandInfo('battery', 'bat', 'show battery level'),
        CommandInfo('legs', 'le', 'show leg and body positions'),
        CommandInfo('parameters', 'par', 'show parameter values or just one selected parameter'),
        CommandInfo('platform', 'pla', 'show hardware platform info'),
        CommandInfo('position', 'po', 'show body position'),
        CommandInfo('servos', 'se', 'show state of all servos'),
    )

    set_commands = (
        CommandInfo('step', 'st', 'enable or disable single-step mode'),
        )

    help_texts = {
        }

    def __init__(self, c: Control):
        self.control = c
        self.words: list[str] = []
        self.step_mode = False
        CommandInterpreter.the_command = self

    def find_keyword(self, commands: tuple[CommandInfo, ...], cmd: str, fn_prefix: str) \
        -> Callable[[CommandInterpreter], None] :
        for c in commands:
            if c.name.startswith(cmd) and cmd.startswith(c.abbrev):
                return getattr(CommandInterpreter, fn_prefix+c.name)
        else:
            raise ValueError(f"unknown or ambiguous keyword '{cmd}'")        

    def execute(self, line: str) -> None:
        self.words = line.lower().split()
        try:
            fn = self.find_keyword(CommandInterpreter.the_commands, self.words[0], 'do_')
        except ValueError:
            raise ValueError(f"unknown or ambiguous command '{self.words[0]}'")
        (fn)(self)

    def help(self, cmds: tuple[CommandInfo, ...]) -> str:
        return '\n'.join([ f'{c.name:10} {c.help}' for c in cmds ])

    def pause(self) -> None:
        if self.step_mode:
            print('press return to continue: ')
            input()

    def check_args(self, minargs: int, maxargs: int = -1) -> None:
        if len(self.words) < minargs + 1:
            raise ValueError(f"too few arguments for command")
        elif len(self.words) > max(minargs, maxargs) + 1:
            raise ValueError(f"too many arguments for command")

    def get_float_arg(self, arg: int) -> float:
        self.check_args(1, 1000)
        try:
            return float(self.words[arg])
        except ValueError:
            raise ValueError(f"expected number, not '{self.words[arg]}'")
                
    def do_help(self) -> None:
        self.check_args(0, 1)
        cmds = None
        if len(self.words) > 1:
            key = self.words[1]
            ht = CommandInterpreter.help_texts.get(key, None)
            if ht:
                print(ht)
                return
            else:
                cmds = getattr(CommandInterpreter, key+'_commands', None)
        else:
            cmds = CommandInterpreter.the_commands
        if cmds:            
            print(self.help(cmds))
        else:
            print(f"Sorry, no help available for '{self.words[1]}'")

    def do_quit(self) -> None:
        raise StopIteration()

    def do_height(self) -> None:
        self.check_args(1)
        self.control.set_height(self.get_float_arg(1))

    def do_posture(self) -> None:
        self.check_args(1)
        self.control.set_posture(self.words[1])

    def do_save(self) -> None:
        self.check_args(0)
        Servo.save_calibration(Params.get_str('calibration_filename'))

    def do_set(self) -> None:
        (self.find_keyword(self.set_commands, self.words[1], 'set_'))(self)        

    def do_servo(self) -> None:
        self.check_args(1,2)
        if len(self.words)==2:
            m = re.match(r'^(.*?)([+-]?\d*)$', self.words[1])
            s, v = m.groups()    #type: ignore[union-attr]
        else:
            s, v = self.words[1], self.words[2]
        self.control.set_servo(s, v)

    def do_show(self) -> None:
        (self.find_keyword(self.show_commands, self.words[1], 'show_'))(self)

    def do_turn(self) -> None:
        self.check_args(2, 3)
        dist = self.get_float_arg(1)
        turn = self.get_float_arg(2)
        dir = self.get_float_arg(3) if len(self.words) > 3 else 0
        self.control.walk(dist, dir) # needs to be updated

    def do_verbose(self) -> None:
        self.check_args(0, 1)
        Logger.to_console(bool(self.get_float_arg(1)) if len(self.words) > 1 else True)

    def do_walk(self) -> None:
        self.check_args(1, 2)
        dist = self.get_float_arg(1)
        dir = self.get_float_arg(2) if len(self.words) > 2 else 0
        self.control.walk(dist, dir)

    def set_step(self) -> None:
        self.check_args(0, 1)
        self.step_mode = bool(self.get_float_arg(1)) if len(self.words) > 1 else True

    def show_battery(self) -> None:
        print(f"Battery level: {Platform.get_battery_level():.2f} V")

    def show_legs(self) -> None:
        self.check_args(1)
        self.show_position()
        print(self.control.body.show_legs())

    def show_platform(self) -> None:
        print(Platform.get_platform_info())

    def show_parameters(self) -> None:
        self.check_args(1, 2)
        pname = '' if len(self.words) < 3 else self.words[2]
        for p in sorted([ pp[0] for pp in Params.enumerate() ]):
            if p==pname or not pname:
                print(f"{p:20} {Params.get_str(p)}")
    
    def show_position(self) -> None:
        self.check_args(1)
        print(f"Body position: {self.control.body.show_position()}")

    def show_servos(self) -> None:
        self.check_args(1)
        print(Servo.show_servos())

        
