#coding:utf-8

from __future__ import annotations
import time
import re
import json
from body import Body
from dataclasses import dataclass
from collections.abc import Callable
from logger import Logger
from servo import Servo
from servo_action import *
from params import Params
from globals import Globals
from robot_platform import RobotPlatform
from robot_keyword import *
from styled_text import StyledText as ST
import time

class CommandInterpreter:

    the_command: CommandInterpreter = None    #type: ignore[assignment]

    the_commands = KeywordTable(
        ('attitude','att', 'set body attitude, \'help attitude\' for more info'),
        ('head', 'hea', 'set head position, 90=straight ahead, 180=down,0=up'),
        ('height', 'hei', 'set height'),
        ('help', 'h', 'get help'),
        ('leg', 'l', 'set leg position explicitly: leg leg-name x y z'),
        ('posture', 'p', 'set static posture'),
        ('quit', 'q', 'terminate program'),
        ('save', 'sav', 'save current position as calibration'),
        ('servo', 'ser', 'modify servo position explicitly'),
        ('set', 'set', 'modify parameter'),
        ('show', 'sh', 'show something'),
        ('speed', 'sp', 'set movement speed, 0=no delays, default=10'),
        ('spread', 'spr', 'set leg spread'),
        ('stretch', 'str', 'set leg stretch'),
        ('turn', 't', 'walk while turning: turn distance angle [direction]'),
        ('verbose', 'v', 'set verbosity level'),
        ('wait', 'wait', 'wait specified time (seconds) (for scripts)'),
        ('walk', 'w', 'walk in straight line: walk distance [direction]'),
        )

    show_commands = KeywordTable(
        ('attitude', 'att', 'show body attitude'),
        ('battery', 'bat', 'show battery level'),
        ('legs', 'le', 'show leg and body positions'),
        ('parameters', 'par', 'show parameter values or just one selected parameter'),
        ('platform', 'pla', 'show hardware platform info'),
        ('position', 'po', 'show body position'),
        ('servos', 'se', 'show state of all servos'),
    )

    set_commands = KeywordTable(
        ('pause', 'pa', 'enable or disable single-step mode'),
        )

    help_texts = KeywordTable(
        ('attitude', 'att', """\
'attitude keyword value' where keyword is one of: normal, backward, forward, height, left, pitch, right, roll, yaw\
        """),
        )

    def __init__(self, b: Body):
        self.body = b
        self.words: list[str] = []
        self.pause_mode = False
        CommandInterpreter.the_command = self

    def find_keyword_fn(self, commands: KeywordTable, cmd: str, fn_prefix: str) \
        -> Callable[[CommandInterpreter], None] :
        return getattr(CommandInterpreter, fn_prefix + commands.find(cmd).name)

    def output(self, text: str) -> None:
        print(ST(text, color='dark_green'))

    def execute(self, line: str) -> None:
        line = line.strip()
        if line:
            if line[0]=='<':
                try:
                    with open(line[1:]) as f:
                        for fline in f.readlines():
                            self.execute(fline[:-1])
                except FileNotFoundError:
                    raise ValueError(f"could not open file '{line[1:]}'")
                except IOError:
                    raise ValueError(f"error reading file '{line[1:]}'")
                except:
                    raise
            elif line[0]!='#':
                self.words = line.lower().split()
                try:
                    fn = self.find_keyword_fn(CommandInterpreter.the_commands, self.words[0], 'do_')
                except ValueError:
                    raise ValueError(f"unknown or ambiguous command '{self.words[0]}'")
                (fn)(self)

    def pause(self) -> bool:
        if self.pause_mode:
            print('press return to continue, q to stop: ', end='')
            text = input()
            if text=='':
                print('')
            elif text[0]=='q':
                raise StopIteration()
        return self.pause_mode

    def help(self, keywords: KeywordTable) -> None:
        return '\n'.join([ str(ST(f'{k.name:12}', color='blue', style='italic') + ST(k.help, color='blue'))
                           for k in keywords ])
        

    def check_args(self, minargs: int, maxargs: int = -1) -> None:
        if len(self.words) < minargs + 1:
            raise ValueError(f"too few arguments for command")
        elif len(self.words) > max(minargs, maxargs) + 1:
            raise ValueError(f"too many arguments for command")

    def get_float_arg(self, arg: int) -> float:
        #self.check_args(1, arg+1)
        try:
            return float(self.words[arg])
        except ValueError:
            raise ValueError(f"expected number, not '{self.words[arg]}'")

    def get_arg(self, arg: int) -> str:
        self.check_args(1, arg+1)
        return self.words[arg]

    def do_attitude(self) -> None:
        self.check_args(2)
        self.body.set_attitude(self.get_arg(1), self.get_float_arg(2))
                
    def do_help(self) -> None:
        self.check_args(0, 1)
        cmds = None
        if len(self.words) > 1:
            key = self.words[1]
            ht = CommandInterpreter.help_texts.find(key, miss_ok=True)
            if ht.name:
                print(ST(ht.help, color='blue'))
                return
            else:
                cmds = getattr(CommandInterpreter, key+'_commands', None)
            if cmds is None:
                try:
                    print(ST(CommandInterpreter.the_commands.find(key).help, color='blue'))
                    return
                except ValueError:
                    pass
        else:
            cmds = CommandInterpreter.the_commands
        if cmds:            
            print(self.help(cmds))
        else:
            print(f"Sorry, no help available for '{self.words[1]}'")

    def do_quit(self) -> None:
        raise EOFError()

    def do_head(self) -> None:
        self.check_args(1)
        pos: float|None = None
        try:
            pos = self.get_float_arg(1)
        except ValueError:
                name = self.get_arg(1)
        with ServoActionList() as actions:
            if pos is None:
                self.body.head.goto_named(name, actions)
            else:                
                self.body.head.goto(pos, actions)

    def do_height(self) -> None:
        self.check_args(1)
        self.body.set_height(self.get_float_arg(1))

    def do_leg(self) -> None:
        self.output(len(self.words), self.words)
        self.check_args(4)
        self.body.set_leg_position(self.words[1],
                                           self.get_float_arg(2),
                                           self.get_float_arg(3),
                                           -abs(self.get_float_arg(4)))
        self.output(self.body.get_leg(self.words[1]).show_position())

    def do_posture(self) -> None:
        self.check_args(1)
        self.body.set_named_posture(self.words[1])

    def do_save(self) -> None:
        self.check_args(0)
        Servo.save_calibration(Params.get_str('calibration_filename'))

    def do_set(self) -> None:
        (self.find_keyword_fn(self.set_commands, self.words[1], 'set_'))(self)        

    def do_servo(self) -> None:
        self.check_args(1,2)
        if len(self.words)==2:
            m = re.match(r'^(.*?)([+-]?\d*)$', self.words[1])
            s, v = m.groups()    #type: ignore[union-attr]
        else:
            s, v = self.words[1], self.words[2]
        m1 = re.match(r'(?:(?:([fr\*])([lr\*]?)([cft]))|(h))', s)
        m2 = re.match(r'([+-]?)(\d+)', v)
        if m1 and m2:
            fr, lr, joint, head = m1.groups()
            diff, angle = m2.groups()
            if fr=='*' and not lr:
                lr = '*'
            if head is None:
                sname = (fr+ lr + joint)
            else:
                sname = 'h'
        elif m1 is None:
            raise ValueError(f"invalid servo identifier '{s}'")
        else:
            raise ValueError(f"invalid servo position '{v}'")                
        self.body.set_servos(s, v)

    def do_show(self) -> None:
        (self.find_keyword_fn(self.show_commands, self.words[1], 'show_'))(self)

    def do_speed(self) -> None:
        self.check_args(1)
        Globals.set('speed', self.get_float_arg(1))

    def do_spread(self) -> None:
        self.check_args(1)
        self.body.set_spread(self.get_float_arg(1))

    def do_stretch(self) -> None:
        self.check_args(1)
        self.body.set_stretch(self.get_float_arg(1))

    def do_turn(self) -> None:
        self.check_args(2, 3)
        dist = self.get_float_arg(1)
        turn = self.get_float_arg(2)
        dir = self.get_float_arg(3) if len(self.words) > 3 else 0
        self.body.walk(dist, dir, turn) # needs to be updated

    def do_verbose(self) -> None:
        self.check_args(0, 1)
        Logger.to_console(bool(self.get_float_arg(1)) if len(self.words) > 1 else True)

    def do_walk(self) -> None:
        self.check_args(1, 2)
        dist = self.get_float_arg(1)
        dir = self.get_float_arg(2) if len(self.words) > 2 else 0
        self.body.walk(dist, dir, 0)

    def do_wait(self) -> None:
        self.check_args(1)
        time.sleep(self.get_float_arg(1))

    def set_pause(self) -> None:
        self.check_args(1, 2)
        self.pause_mode = bool(self.get_float_arg(2)) if len(self.words) > 2 else True

    def show_attitude(self) -> None:
        self.check_args(1)
        self.output(self.body.show_attitude())

    def show_battery(self) -> None:
        self.output(f"Battery level: {RobotPlatform.get_battery_level():.2f} V")

    def show_legs(self) -> None:
        self.check_args(1)
        self.show_position()
        self.output(self.body.show_legs())

    def show_platform(self) -> None:
        self.output(RobotPlatform.get_platform_info())

    def show_parameters(self) -> None:
        self.check_args(1, 2)
        pname = '' if len(self.words) < 3 else self.words[2]
        for p in sorted([ pp[0] for pp in Params.enumerate() ]):
            if p==pname or not pname:
                self.output(f"{p:20} {Params.get_str(p)}")
    
    def show_position(self) -> None:
        self.check_args(1)
        self.output(f"Body position: {self.body.show_position()}")

    def show_servos(self) -> None:
        self.check_args(1)
        self.output(Servo.show_servos())

        
