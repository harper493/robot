
#coding:utf-8

from __future__ import annotations
from ADS7830 import ADS7830
from robot_imu import Imu, ImuAngles
from geometry import *

class RobotPlatformBase:

    def get_battery_level(self) -> float:
        return 0

    def get_platform_info(self) -> str:
        return 'Platform type: Software only running on Linux'

    def get_model_info(self) -> str:
        return ''

    def get_imu_angles(self) -> ImuAngles:
        return ImuAngles()

    def get_imu_position(self) -> Point:
        return Point()

    def stop(self) -> None:
        pass

class RobotPlatform:

    the_platform: RobotPlatformBase

    @staticmethod
    def init(_type: str='') -> RobotPlatformBase:
        try:
            RobotPlatform.the_platform = (platform_types[_type or RobotPlatform.get_type()])()
            return RobotPlatform.the_platform
        except KeyError:
            raise ValueError(f"unknown platform type '{_type}'")

    @staticmethod
    def get_battery_level() -> float:
        return RobotPlatform.the_platform.get_battery_level()

    @staticmethod
    def get_platform_info() -> str:
        return RobotPlatform.the_platform.get_platform_info()

    @staticmethod
    def get_type() -> str:
        try:
            with open('/proc/device-tree/serial-number') as f:
                serial = f.read()[:-1]
        except:
            serial = ''
        if serial=='100000000432b6fc':
            result = 'quad'
        else:
            result = 'none'
        return result

    @staticmethod
    def get_imu_angles() -> ImuAngles:
        return RobotPlatform.the_platform.get_imu_angles()

    @staticmethod
    def get_imu_position() -> Point:
        return RobotPlatform.the_platform.get_imu_position()

    @staticmethod
    def stop() -> None:
        return RobotPlatform.the_platform.stop()

class RobotPlatformRaspberryPi(RobotPlatformBase):    

    def get_model_info(self) -> str:
        try:
            with open('/proc/device-tree/model') as f:
                return f.read()[:-1]
        except:
            return ''

class RobotPlatformQuad(RobotPlatformRaspberryPi):

    def __init__(self):
        Imu.init()

    def get_battery_level(self) -> float:
        return ADS7830().readAdc(0)/255 * 10

    def get_platform_info(self) -> str:
        return f'Platform type: Freenove Quadraped running on {self.get_model_info()}'

    def get_imu_angles(self) -> ImuAngles:
        return Imu.get_angles()

    def get_imu_position(self) -> Point:
        return Imu.get_position()

    def stop(self) -> None:
        Imu.stop()

platform_types = {
    "quad" : RobotPlatformQuad,
    "none" : RobotPlatformBase
    }
        
