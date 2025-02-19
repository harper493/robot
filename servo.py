#coding:utf-8

from __future__ import annotations
from PCA9685 import PCA9685
import time
import json

the_servos: dict[int, Servo] = {}

the_pwm =  PCA9685(address=0x40, debug=True)
the_pwm.setPWMFreq(50)

servo_type = None

MAX_ANGLE = 162.0
MIN_ANGLE = 18.0

LOW_POS = 102.0
HIGH_POS = 512.0
    
class Servo:

    def __init__(self, chan: int, reverse: bool):
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
        pass

    def get_angle(self) -> float:
        return self.position

    def adjust_angle(self, delta: float) -> None:
        self.set_angle(self.position + delta)

    @staticmethod
    def get(chan: int) -> Servo:
        return the_servos[chan]

    @staticmethod
    def enroll(chan: int, reverse: bool) -> Servo:
        the_servos[chan] = Servo.factory(chan, reverse)
        return the_servos[chan]

    @staticmethod
    def load_calibration(filename: str) -> None:
        try:
            with open(filename) as f:
                data = f.read()
        except:
            return
        for ch,v in json.loads(data).items():
            Servo.get(int(ch)).calibration = float(v)

    @staticmethod
    def save_calibration(filename: str) -> None:
        calibration = { s.channel : (s.position - 90 + s.calibration)
                                     for s in the_servos.values() }
        with open(filename, 'w') as f:
            f.write(json.dumps(calibration, indent=4))
            f.write('\n')

    @staticmethod
    def set_servo_angle(chan: int, angle: float) -> None:
        Servo.get(chan).set_angle(angle)

    @staticmethod
    def factory(chan: int, reverse: bool) -> Servo:
        if servo_type:
            return servo_type(chan, reverse)
        else:
            return Servo(chan, reverse)

    @staticmethod
    def set_servo_type(t: str) -> None:
        global servo_type
        try: 
            servo_type = type_map[t]
        except KeyError:
            raise ValueError(f"unknown servo type '{t}'")

class PWMServo(Servo):

    def __init__(self, chan: int, reverse: bool):
        super(PWMServo, self).__init__(chan, reverse)

    def set_angle(self, angle: float) -> None:
        rev_angle = 180 - angle if self.reverse else angle
        true_angle = min(max(rev_angle, MIN_ANGLE), MAX_ANGLE) + self.calibration
        #print(self.channel, self.reverse, angle, self.calibration, true_angle)
        self.position = angle
        data = self.map(true_angle, 0, 180, LOW_POS, HIGH_POS)
        the_pwm.setPWM(self.channel, 0, int(data))

type_map = { 'pwm' : PWMServo,
             'none' : Servo,
             }

                        
            
       
        
        
 
