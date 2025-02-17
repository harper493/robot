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

    def __init__(self, chan: int, calib: float = 0.0):
        self.position = 90.0
        self.channel = chan
        self.calibration = calib
#        
#Convert the input angle to the value of pca9685
#
    def map(self, value: float, fromLow: float, fromHigh: float, toLow: float, toHigh: float) -> float:
        return (toHigh-toLow)*(value-fromLow) / (fromHigh-fromLow) + toLow

    def set_angle(self, angle: float) -> None:
        pass

    @staticmethod
    def enroll(chan: int) -> Servo:
        try:
            result = the_servos[chan]
        except KeyError:
            result = Servo.factory(chan)
            the_servos[chan] = result
        return result

    @staticmethod
    def load_calibration(filename: str) -> None:
        with open(filename) as f:
            data = f.read()
        for ch,v in json.loads(data):
            Servo.enroll(int(ch)).calibration = float(v)

    @staticmethod
    def save_calibration(filename: str) -> None:
        calibration = { s.channel : (s.position - 90 + s.calibration)
                                     for s in the_servos.values() }
        with open(filename, 'w') as f:
            f.write(json.dumps(calibration))
        f.write('\n')

    @staticmethod
    def set_servo_angle(chan: int, angle: float) -> None:
        Servo.enroll(chan).set_angle(angle)

    @staticmethod
    def factory(chan: int, calib: int = 0) -> Servo:
        if servo_type:
            return servo_type(chan, calib)
        else:
            return Servo(chan, calib)

    @staticmethod
    def set_servo_type(t: str) -> None:
        servo_type = type_map[t] if t else Servo

class PWMServo(Servo):

    def __init__(self, chan: int, calib: float = 0.0):
        super(PWMServo, self).__init__(chan, calib)

    def set_angle(self, angle: float) -> None:
        angle = min(max(angle, MIN_ANGLE), MAX_ANGLE)
        self.position = angle
        data = self.map(angle, 0, 180, LOW_POS, HIGH_POS)
        the_pwm.setPWM(self.channel, 0, int(data))

type_map = { 'PWM' : PWMServo,
             }

                        
            
       
        
        
 
