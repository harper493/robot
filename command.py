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

@dataclass
class CommandInfo:
    name: str
    abbrev: str
    help: str

class CommandInterpreter:

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
        CommandInfo('legs', 'le', 'show leg and body positions'),
        CommandInfo('position', 'po', 'show body position'),
    )

    def __init__(self, c: Control):
        self.control = c
        self.words: list[str] = []

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
        return '\n'.join([ f'{c.name:8} {c.help}' for c in cmds ])

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
        print(self.help(CommandInterpreter.the_commands))

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

    def do_servo(self) -> None:
        self.check_args(1,2)
        if len(self.words)==2:
            m = re.match(r'^(.*?)([+-]?\d*)$', self.words[1])
            s, v = m.groups()    #type: ignore[union-attr]
        else:
            s, v = self.words[1], self.words[2]
        self.control.set_servo(s, v)

    def do_show(self) -> None:
        self.check_args(1)
        fn = self.find_keyword(self.show_commands, self.words[1], 'show_')
        (fn)(self)

    def do_turn(self) -> None:
        self.check_args(2, 3)
        dist = self.get_float_arg(1)
        turn = self.get_float_arg(2)
        dir = self.get_float_arg(3) if len(self.words) > 3 else 0
        self.control.walk(dist, dir) # needs to be updated

    def do_verbose(self) -> None:
        self.check_args(1)
        Logger.to_console(bool(self.get_float_arg(1)))

    def do_walk(self) -> None:
        self.check_args(1, 2)
        dist = self.get_float_arg(1)
        dir = self.get_float_arg(2) if len(self.words) > 2 else 0
        self.control.walk(dist, dir)

    def show_legs(self) -> None:
        self.show_position()
        print(self.control.body.show_legs())
    
    def show_position(self) -> None:
        print(f"Body position: {self.control.body.show_position()}")

        
        

r"""
def do_servo(cmd):
    do_servo_command(cmd)
    exec_servo()

def do_servo_command(cmd) :
    m = re.match(r'([fr][lr]|h|\*)([hkt]?) *([+-]?)(\d+)', cmd)
    if m:
        leg, joint, diff, angle = m.groups()
        if leg=='*':
            for l in leg_map.keys():
                set_joint(l, joint, diff, angle)
        else:
            set_joint(leg, joint, diff, angle)
    else:
        print("Unknown command, format is [fr][lr][hkt]<angle>")

def set_joint(leg, joint, diff, angle):
    s = servo_map[leg]
    if leg=='h':
        j = 0
    elif s < 8:
        j = joint_map[joint]
    else:
        j = -joint_map[joint]
    channel = s + j
    if diff:
        angle = get_angle(channel) + int(diff + angle)
    else:
        angle = int(angle)
    set_servo(channel, angle)

def do_relax(cmd='relax'):
    do_servo_command("*h90")
    do_servo_command("*k90")
    do_servo_command("*t90")
    do_servo_command("h90")
    exec_servo()

def do_sleep(cmd):
    do_servo_command("*h100")
    do_servo_command("*k20")
    do_servo_command("*t20")
    exec_servo()

def do_stand(cmd):
    do_servo_command("*h105")
    do_servo_command("*t45")
    do_servo_command("*k90")
    exec_servo()

def do_sit(cmd):
    do_servo_command("frh105")
    do_servo_command("frt45")
    do_servo_command("frk110")
    do_servo_command("flh105")
    do_servo_command("flt45")
    do_servo_command("flk110")
    do_servo_command("rlh100")
    do_servo_command("rlt20")
    do_servo_command("rlk50")
    do_servo_command("rrh100")
    do_servo_command("rrt20")
    do_servo_command("rrk50")
    exec_servo()

def do_bow(cmd):
    do_servo_command("frh100")
    do_servo_command("frt20")
    do_servo_command("frk30")
    do_servo_command("flh100")
    do_servo_command("flt20")
    do_servo_command("flk30")
    do_servo_command("rlh105")
    do_servo_command("rlt45")
    do_servo_command("rlk110")
    do_servo_command("rrh105")
    do_servo_command("rrt50")
    do_servo_command("rrk110")
    exec_servo()

def do_sprawl(cmd):
    do_servo_command("*t90")
    do_servo_command("*k10")
    do_servo_command("*h160")
    exec_servo()
    
def do_save(cmd):
    calibration = { ch:(v-90+get_calib(ch)) for ch,v in angles.items() }
    with open(calib_filename, 'w') as f:
        f.write(json.dumps(calibration))
        f.write('\n')

def do_bat(cmd):
    volts = ADS7830().readAdc(0)/255 * 10
    print(f'Battery voltage is {volts:.2f}\n')

def set_servo(chan, angle):
    angles[chan] = angle
    calib = get_calib(chan)
    true_angle = angle + calib
    print(chan, angle, calib, true_angle)
    if chan < 8:
        angle = 180 - angle
    servo.add(chan, angle + calib)

def exec_servo():
    servo.exec()

def get_angle(chan):
    return angles.get(chan, 90)

def get_calib(chan):
    return calibration.get(chan, 0)

def load_calib():
    global calibration
    try:
        with open(calib_filename) as f:
            calibration = { int(ch):int(v) for ch,v in json.loads(f.read()).items() }
    except:
        pass
        
commands = { 'bat' : do_bat,
             'bow' : do_bow,
             'save' : do_save,
             'relax' : do_relax,
             'sit' : do_sit,
             'sprawl' : do_sprawl,
             'stand' : do_stand,
             'sleep' : do_sleep }

def main():
    load_calib()
    do_relax('relax')
    while True:
        print('Command: ', end='')
        try:
            cmd = input()
        except:
            break
        if cmd:
            cmd = cmd.lower()
            commands.get(cmd.split()[0], do_servo)(cmd)
        else:
            break

main()        
"""    

        
        
        
        
