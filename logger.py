#coding:utf-8

import logging

class Logger:

    the_logger = None

    def __init__(self):
        self.my_logger = logging.getLogger('')
        logging.basicConfig(format='%(levelname)s: %(message)s',
                            level=logging.DEBUG,
                            filename='log.txt')

    @staticmethod
    def info(text: str) -> None:
        Logger.the_logger.my_logger.info(text)

    @staticmethod
    def debug(text: str) -> None:
        Logger.the_logger.my_logger.debug(text)

    @staticmethod
    def warn(text: str) -> None:
        Logger.the_logger.my_logger.warn(text)

    @staticmethod
    def error(text: str) -> None:
        Logger.the_logger.my_logger.error(text)

    @staticmethod
    def init() -> None:
        Logger.the_logger = Logger()
        Logger.info("Logger initialised")
        

        
