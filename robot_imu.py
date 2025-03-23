#coding:utf-8

from __future__ import annotations
from IMU import IMU
from threading import Thread
from geometry import *
import time
try:
    from mpu6050 import mpu6050    #type: ignore[import-untyped]
except ImportError:
    mpu6050 = None

class Imu:

    the_imu: Imu = None    #type: ignore[assignment]

    def __init__(self, interval=0.01):
        Imu.the_imu = self
        self.interval = interval
        self.angles = Angles()
        self.velocity = Point()
        self.position = Point()
        self.a_calib = Point()
        self.g_calib = Angles()
        self.a_total = Point()
        self.g_total = Angles()
        self.count = 0
        self.sensor: mpu6050 = mpu6050(address=0x68) if mpu6050 else None #type: ignore[assign]
        self.my_thread = Thread(target=lambda: self.run())
        self.stopping = False
        self.last_time = time.monotonic()
        self.last_print = time.monotonic()
        self.my_thread.start()
        
    def run(self) -> None:
        if self.sensor:
            for i in range(1000):
                self.a_calib += Point(*[ v for v in self.sensor.get_accel_data().values() ]) / 1000.0
                self.g_calib += Angles(*[ v for v in self.sensor.get_gyro_data().values() ]) / 1000.0
                time.sleep(0.001)
            #print(self.a_calib, self.g_calib)
        while not self.stopping:
            if self.sensor:
                now = time.monotonic()
                delta = now - self.last_time
                self.last_time = now
                a = Point(*[ v for v in self.sensor.get_accel_data().values() ])
                g = Angles(*[ v for v in self.sensor.get_gyro_data().values() ])
                a -= self.a_calib
                g -= self.g_calib
                self.a_total += a
                self.g_total += g
                self.count += 1
                self.velocity = self.velocity + a * delta
                self.angles = self.angles + g * delta
                self.position = self.position + self.velocity * delta * 100.0
                if False and now - self.last_print > 1.0:
                    print(a, g,
                          self.velocity, self.position, self.angles)
                    self.last_print = now
            time.sleep(self.interval)

    @staticmethod
    def get_angles() -> Angles:
        return Imu.the_imu.angles

    @staticmethod
    def get_position() -> Point:
        return Imu.the_imu.position

    @staticmethod
    def init() -> None:
        Imu()

    @staticmethod
    def stop() -> None:
        Imu.the_imu.stopping = True
        Imu.the_imu.my_thread.join()

    
