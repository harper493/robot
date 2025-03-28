#!/usr/bin/python
#coding:utf-8

from __future__ import annotations
from body import *
from params import *
from leg import *
from logger import Logger
from servo import Servo
from servo_action import *
from command import CommandInterpreter
from robot_platform import RobotPlatform
from styled_text import StyledText as ST
try:
    import readline
except ImportError :
    readline = None     #type: ignore[assignment]

parameter_defaults = {
    "body_type" : "quad",
    "head_type" : "simple",
    "servo_type" : "pwm",
    "clear_height" : "0.5",
    "default_step_height" : "3",
    "default_height" : "7",
    "default_speed" : "10.0",
    "max_servo_iteration" : "5",
    "femur_length" : "5.3",
    "tibia_length" : "6.0",
    "default_step_size" : "3",
    "small_step_size" : "0.8",
    "leg_fl_servo_cox" : "4",
    "leg_fl_servo_femur" : "3",
    "leg_fl_servo_tibia" : "2",
    "leg_fr_servo_cox" : "11",
    "leg_fr_servo_femur" : "12",
    "leg_fr_servo_tibia" : "13",
    "leg_rl_servo_cox" : "7",
    "leg_rl_servo_femur" : "6",
    "leg_rl_servo_tibia" : "5",
    "leg_rr_servo_cox" : "8",
    "leg_rr_servo_femur" : "9",
    "leg_rr_servo_tibia" : "10",
    "leg_fl_x" : "5.3",
    "leg_fl_y" : "5.0",
    "leg_fl_z" : "0",
    "leg_fr_x" : "5.3",
    "leg_fr_y" : "-5.0",
    "leg_fr_z" : "0",
    "leg_rl_x" : "-8.3",
    "leg_rl_y" : "5.0",
    "leg_rl_z" : "0",
    "leg_rr_x" : "-8.3",
    "leg_rr_y" : "-5.0",
    "leg_rr_z" : "0",
    "head_servo" : "15",
    "gait_default" : "fl,rl,rr,fr",
    "posture_stand" : "fl:2 -1.0 7, fr:2 -1.0 7, rl:0.3 -1 7, rr:0.3 -1 7",
    "posture_relax" : "6 0.0 6",
    "posture_high" : "fl:2.5 -1.5 10.5, fr:2.5 -1.5 10.5, rl:-1 -1.5 10.5, rr:-1 -1.5 10.5",
    "posture_low" : "1.1 -1.2 4",
    "posture_sleep" : "fl:x=4 z=0.3, fr:x=4 z=0.3, rl:x=0 z=0.3, rr:x=0 z=0.3",
    "posture_sit" : "fl:x=-2.9 y=-0.2 z=3, fr:x=-2.9 y=-0.2 z=3, rl:x=3.5 y=0 z=0.2, rr: x=3.5 y=0 z=0.2",
    "calibration_filename" : "calib.txt",
    "balance_lateral_offset" : "1.2",
    "balance_long_offset" : "0.0",
    }

def run(body: Body) -> None:
    interpreter = CommandInterpreter(body)
    while True:
        print('robot> ', end='')
        try:
            cmd = input()
        except:
            print('')
            break
        if cmd:
            try:
                interpreter.execute(cmd)
            except EOFError:
                break
            except (ValueError, IOError) as exc:
                print(ST("Error: ", color='red', style='bold') + ST(str(exc.args[0]), color='red'))
            except StopIteration:
                pass
        else:
            print('')
    RobotPlatform.stop()        

def init() -> Body:
    Params.load('parameters.txt', parameter_defaults)
    Globals.init()
    Logger.init('log.txt')
    RobotPlatform.init()
    Servo.set_servo_type(Params.get_str('servo_type'))
    body = Body.make_body(Params.get_str('body_type'))
    Servo.load_calibration(Params.get_str('calibration_filename'))   # must come AFTER body creation
    body.set_named_posture('relax')
    with ServoActionList() as actions:
        body.head.goto_named('default', actions)
    return body

if __name__ == '__main__':
    run(init())

