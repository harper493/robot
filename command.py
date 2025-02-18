#coding:utf-8

import time
import re
import json
from control import Control
from dataclasses import dataclass
from collections.abc import Callable

leg_map = { 'fl':2, 'rl':5, 'rr': 8, 'fr':11 }
servo_map = { 'fl':2, 'rl':5, 'rr': 10, 'fr':13, 'h':15 }
joint_map = { 'h':2, 't':1, 'k':0 }
angles = {}
calibration = {}

calib_filename = 'calib.txt'

@dataclass
class CommandInfo:
    name: str
    abbrev: str
    help: str

class CommandInterpreter:

    the_commands = (
        CommandInfo('height', 'he', 'set height'),
        CommandInfo('help', 'h', 'get help'),
        CommandInfo('leg', 'l', 'set leg position explicitly'),
        CommandInfo('posture', 'p', 'set static posture'),
        CommandInfo('quit', 'q', 'terminate program'),
        CommandInfo('servo', 'ser', 'modify servo position explicitly'),
        CommandInfo('set', 'set', 'modify parameter'),
        CommandInfo('show', 'sh', 'show something'),
        CommandInfo('turn', 't', 'walk while turning'),
        CommandInfo('walk', 'w', 'walk in straight line'),
        )

    def __init__(self, c: Control):
        self.control = c

    def find_keyword(self, commands: tuple[CommandInfo], cmd: str, fn_prefix: str) \
        -> Callable[[list[str]], None] :
        for c in commands:
            if c.name.startswith(cmd) and cmd.startswith(c.abbrev):
                return getattr(CommandInterpreter, fn_prefix+c.name)
        else:
            raise ValueError()        

    def execute(self, line: str) -> None:
        words = line.lower().split()
        try:
            fn = self.find_keyword(CommandInterpreter.the_commands, words[0], 'do_')
        except ValueError:
            raise ValueError(f"unknown or ambiguous command '{words[0]}'")
        (fn)(self, words)

    def help(self, cmds: tuple[CommandInfo]) -> str:        
        return '\n'.join([ f'{c.name:8} {c.help}' for c in cmds ])
    
    def do_help(self, words: list[str]) -> None:
        print(self.help(CommandInterpreter.the_commands))

    def do_quit(self, words: list[str]) -> None:
        raise StopIteration()

    def do_height(self, words: list[str]) -> None:
        print('not yet')

    def do_posture(self, words: list[str]) -> None:
        self.control.set_named_posture(words[1])

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

        
        
        
        
