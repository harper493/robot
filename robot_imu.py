#coding:utf-8

from __future__ import annotations
from IMU import IMU
from threading import Thread
from dataclasses import dataclass
import time

@dataclass
class ImuData:
    roll: float = 0
    pitch: float = 0
    yaw: float = 0

class Imu:

    the_imu: Imu = None

    def __init__(self, interval=0.1):
        Imu.the_imu = self
        self.interval = interval
        self.data = ImuData()
        self.my_imu = IMU()
        self.my_thread = Thread(target=Imu.run_thread)
        self.stopping = False
        self.my_thread.start()
        
    def run(self):
        while not self.stopping:
            self.data = ImuData(*self.my_imu.imuUpdate())
            #print(self.data)
            time.sleep(self.interval)

    @staticmethod
    def run_thread():
        Imu.the_imu.run()

    @staticmethod
    def get():
        return Imu.the_imu.data

    @staticmethod
    def init():
        Imu()

    @staticmethod
    def stop():
        Imu.the_imu.stopping = True
        Imu.the_imu.my_thread.join()

    
