#!/usr/bin/python
#coding:utf-8

from __future__ import annotations
from control import *
from body import *
from params import *
from leg import *
from logger import Logger
from servo import Servo
from command import CommandInterpreter
from platform import Platform

try:
    import readline
except ImportError :
    readline = None     #type: ignore[assignment]

parameter_defaults = {
    "body_type" : "quad",
    "servo_type" : "pwm",
    "clear_height" : "0.3",
    "default_step_height" : "0.5",
    "default_height" : "2.5",
    "default_speed" : "200.0",
    "femur_length" : "2",
    "tibia_length" : "2.3",
    "default_step_size" : "1",
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
    "gait_default" : "fl,rr,fr,rl",
    "posture_stand" : "0.5 -1.0 2.3 0 0 0",
    "posture_relax" : "2.3 0.0 2.0 0 0 0",
    "calibration_filename" : "calib.txt"
    }

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
    Params.load('parameters.txt', parameter_defaults)
    Logger.init('log.txt')
    Platform.factory()
    Servo.set_servo_type(Params.get_str('servo_type'))
    body = Body.make_body(Params.get_str('body_type'))
    Servo.load_calibration(Params.get_str('calibration_filename'))   # must come AFTER body creation
    return Control(body)

if __name__ == '__main__':
    run(init())

