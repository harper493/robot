#!/usr/bin/python
#coding:utf-8

from __future__ import annotations
from control import *
from body import *
from params import *
from leg import *
from logger import Logger
from servo import Servo
from servo_action import *
from command import CommandInterpreter
from robot_platform import RobotPlatform

try:
    import readline
except ImportError :
    readline = None     #type: ignore[assignment]

parameter_defaults = {
    "body_type" : "quad",
    "head_type" : "simple",
    "servo_type" : "pwm",
    "clear_height" : "0.7",
    "default_step_height" : "0.9",
    "default_height" : "2.5",
    "default_speed" : "10.0",
    "max_servo_iteration" : "5",
    "femur_length" : "2",
    "tibia_length" : "2.3",
    "default_step_size" : "1",
    "small_step_size" : "0.3",
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
    "leg_fl_x" : "85",
    "leg_fl_y" : "50",
    "leg_fl_z" : "0",
    "leg_fr_x" : "85",
    "leg_fr_y" : "-50",
    "leg_fr_z" : "0",
    "leg_rl_x" : "-90",
    "leg_rl_y" : "50",
    "leg_rl_z" : "0",
    "leg_rr_x" : "-90",
    "leg_rr_y" : "-50",
    "leg_rr_z" : "0",
    "head_servo" : "15",
    "gait_default" : "fl,rr,fr,rl",
    "posture_stand" : "fl:1.8 -1.0 2.5, fr:1.8 -1.0 2.5, rl:0 -1 2.5, rr:0 -1 2.5",
    "posture_relax" : "2.3 0.0 2.0",
    "posture_high" : "1.0 -0.8 3.0",
    "posture_low" : "1.1 -1.2 2.1 0 0 0",
    "posture_sleep" : "fl:x=4 z=0.3, fr:x=4 z=0.3, rl:x=0 z=0.3, rr:x=0 z=0.3",
    "calibration_filename" : "calib.txt"
    }

def run(control: Control) -> None:
    interpreter = CommandInterpreter(control)
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
            except ValueError as exc:
                print("Error:", str(exc.args[0]))
            except StopIteration:
                pass
        else:
                print('')

def init() -> Control:
    Params.load('parameters.txt', parameter_defaults)
    Globals.init()
    Logger.init('log.txt')
    RobotPlatform.factory()
    Servo.set_servo_type(Params.get_str('servo_type'))
    body = Body.make_body(Params.get_str('body_type'))
    Servo.load_calibration(Params.get_str('calibration_filename'))   # must come AFTER body creation
    control = Control(body)
    control.set_posture('relax')
    with ServoActionList() as actions:
        body.head.goto_named('default', actions)
    return control

if __name__ == '__main__':
    run(init())

