#coding:utf-8

from __future__ import annotations
from IMU import IMU
from threading import Thread
from geometry import *
from dataclasses import dataclass
import time

@dataclass
class ImuAngles:
    roll: float = 0
    pitch: float = 0
    yaw: float = 0

class Imu:

    the_imu: Imu = None    #type: ignore[assignment]

    def __init__(self, interval=0.01):
        Imu.the_imu = self
        self.interval = interval
        self.angles = ImuAngles()
        self.my_imu = IMU()
        self.my_thread = Thread(target=Imu.run_thread)
        self.stopping = False
        self.my_thread.start()
        
    def run(self) -> None:
        while not self.stopping:
            self.angles = ImuAngles(*self.my_imu.imuUpdate())
            #print(self.data)
            time.sleep(self.interval)

    @staticmethod
    def run_thread() -> None:
        Imu.the_imu.run()

    @staticmethod
    def get_angles() -> ImuAngles:
        return Imu.the_imu.angles

    @staticmethod
    def get_position() -> Point:
        imu = Imu.the_imu.my_imu
        return Point(imu.exInt, imu.eyInt, imu.ezInt)

    @staticmethod
    def init() -> None:
        Imu()

    @staticmethod
    def stop() -> None:
        Imu.the_imu.stopping = True
        Imu.the_imu.my_thread.join()

    
