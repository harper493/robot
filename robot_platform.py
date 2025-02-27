
#coding:utf-8

from __future__ import annotations
from ADS7830 import ADS7830

class RobotPlatformBase:

    def get_battery_level(self) -> float:
        return 0

    def get_platform_info(self) -> str:
        return 'Platform type: Software only running on Linux'

    def get_model_info(self) -> str:
        return ''

class RobotPlatform:

    the_platform: RobotPlatformBase

    @staticmethod
    def factory(_type: str='') -> RobotPlatformBase:
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

class RobotPlatformRaspberryPi(RobotPlatformBase):    

    def get_model_info(self) -> str:
        try:
            with open('/proc/device-tree/model') as f:
                return f.read()[:-1]
        except:
            return ''

class RobotPlatformQuad(RobotPlatformRaspberryPi):

    def get_battery_level(self) -> float:
        return ADS7830().readAdc(0)/255 * 10

    def get_platform_info(self) -> str:
        return f'Platform type: Freenove Quadraped running on {self.get_model_info()}'

platform_types = {
    "quad" : RobotPlatformQuad,
    "none" : RobotPlatformBase
    }
        
