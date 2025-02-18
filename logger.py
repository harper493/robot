#coding:utf-8

from __future__ import annotations
import logging
import datetime
import os

the_logger: Logger

class Logger:

    def __init__(self, filename: str='log.txt'):
        try:
            os.remove(filename)
        except:
            pass
        self.my_logger = logging.getLogger('')
        logging.basicConfig(format='%(levelname)s: %(message)s',
                            level=logging.DEBUG,
                            filename=filename)

    @staticmethod
    def info(text: str) -> None:
        the_logger.my_logger.info(text)

    @staticmethod
    def debug(text: str) -> None:
        the_logger.my_logger.debug(text)

    @staticmethod
    def warn(text: str) -> None:
        the_logger.my_logger.warn(text)

    @staticmethod
    def error(text: str) -> None:
        the_logger.my_logger.error(text)

    @staticmethod
    def init(filename: str='log.txt') -> None:
        global the_logger
        the_logger = Logger(filename)
        Logger.info(f"Logger initialised at {datetime.datetime.now()}")
        

        
