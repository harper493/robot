#coding:utf-8

from __future__ import annotations
from ADS7830 import ADS7830

class PlatformBase:

    def get_battery_level(self) -> float:
        return 0

    def get_platform_info(self) -> str:
        return 'Platform type: Software only running on Linux'

class Platform:

    the_platform: Platform

    @staticmethod
    def factory(_type: str='') -> Platform:
        try:
            Platform.the_platform = (platform_types[_type or Platform.get_type()])()
            return Platform.the_platform
        except KeyError:
            raise ValueError(f"unknown platform type '{_type}'")

    @staticmethod
    def get_battery_level() -> float:
        return Platform.the_platform.get_battery_level()

    @staticmethod
    def get_platform_info() -> str:
        return Platform.the_platform.get_platform_info()


    @staticmethod
    def get_type() -> str:
        try:
            with open('/proc/device-tree/serial-number') as f:
                serial = f.read()
        except:
            serial = ''
        print(serial)
        if serial=='100000000432b6fc':
            return 'quad'
        else:
            return 'none'

class PlatformQuad(PlatformBase):

    def get_battery_level(self) -> Float:
        return ADS7830().readAdc(0)/255 * 10

    def get_platform_info(self) -> str:
        return 'Platform type: Freenove Quadraped running on Raspberry Pi'

platform_types = {
    "quad" : PlatformQuad,
    "none" : PlatformBase
    }
        
