#coding:utf-8

from __future__ import annotations
from PCA9685 import PCA9685
import time
import json
from logger import Logger

the_servos: dict[int, Servo] = {}

the_pwm =  PCA9685(address=0x40, debug=True)
the_pwm.setPWMFreq(50)

servo_type = None

MAX_ANGLE = 162.0
MIN_ANGLE = 18.0

LOW_POS = 102.0
HIGH_POS = 512.0
    
class Servo:

    def __init__(self, name: str, chan: int, reverse: bool):
        self.name = name
        self.position = 90.0
        self.channel = chan
        self.calibration = 0.0
        self.reverse = reverse
#        
#Convert the input angle to the value of pca9685
#
    def map(self, value: float, fromLow: float, fromHigh: float, toLow: float, toHigh: float) -> float:
        return (toHigh-toLow)*(value-fromLow) / (fromHigh-fromLow) + toLow

    def set_angle(self, angle: float) -> None:
        self.position = angle
        pass

    def get_position(self) -> float:
        return self.position

    def adjust_angle(self, delta: float) -> None:
        self.set_angle(self.position + delta)

    def calibrate(self) -> float:
        self.calibration = self.position - 90 + self.calibration
        return self.calibration

    def show(self) -> str:
        return (f"{self.name.upper():3} chan {str(self.channel) + ('R' if self.reverse else ' '):3}" +
                f' angle {round(self.position, 1):6}' +
                f' true angle {round(self.true_angle, 1):6} calib {round(self.calibration, 1):6}')

    @staticmethod
    def get(chan: int) -> Servo:
        return the_servos[chan]

    @staticmethod
    def enroll(name: str, chan: int, reverse: bool) -> Servo:
        the_servos[chan] = Servo.factory(name, chan, reverse)
        return the_servos[chan]

    @staticmethod
    def load_calibration(filename: str) -> None:
        try:
            with open(filename) as f:
                data = f.read()
        except:
            return
        for ch,v in json.loads(data).items():
            try:
                Servo.get(int(ch)).calibration = float(v)
            except (KeyError, ValueError):
                pass

    @staticmethod
    def save_calibration(filename: str) -> None:
        calibration = { s.channel : s.calibrate()
                        for s in the_servos.values() }
        with open(filename, 'w') as f:
            f.write(json.dumps(calibration, indent=4))
            f.write('\n')

    @staticmethod
    def set_servo_angle(chan: int, angle: float) -> None:
        Servo.get(chan).set_angle(angle)

    @staticmethod
    def factory(name: str, chan: int, reverse: bool) -> Servo:
        if servo_type:
            return servo_type(name, chan, reverse)
        else:
            return Servo(name, chan, reverse)

    @staticmethod
    def set_servo_type(t: str) -> None:
        global servo_type
        try: 
            servo_type = type_map[t]
        except KeyError:
            raise ValueError(f"unknown servo type '{t}'")

    @staticmethod
    def get_servos() -> dict[int, Servo]:
        return the_servos

    @staticmethod
    def show_servos() -> str:
        return '\n'.join([ s.show() for s in the_servos.values() ])

class PWMServo(Servo):

    def __init__(self, name: str, chan: int, reverse: bool):
        super(PWMServo, self).__init__(name, chan, reverse)

    def set_angle(self, angle: float) -> None:
        calib_angle = angle + self.calibration
        rev_angle = round(180 - calib_angle if self.reverse else calib_angle, 1)
        self.true_angle = round(min(max(rev_angle, MIN_ANGLE), MAX_ANGLE), 1)
        self.position = angle
        command = round(self.map(self.true_angle, 0, 180, LOW_POS, HIGH_POS), 1)
        the_pwm.setPWM(self.channel, 0, int(command))
        if False:
            Logger.info(f'servo.set_angle {self.channel} {self.name.upper()} angle {round(angle, 1)}'
                        f' {rev_angle=} calib {self.calibration} true angle {self.true_angle=}'
                        f' {command=}')

type_map = { 'pwm' : PWMServo,
             'none' : Servo,
             }

       
        
        
 
