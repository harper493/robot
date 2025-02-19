#coding:utf-8

from __future__ import annotations

import logging
import datetime
import os

use_console: bool = False
the_file: _io.TextIOWrapper = None    #type: ignore[assignment, name-defined]

class Logger:

    DEBUG = 1
    INFO = 2
    WARN = 3
    ERROR = 4
    FATAL = 5

    def __init__(self, filename: str='log.txt'):
        try:
            os.remove(filename)
        except:
            pass
        self.my_logger = logging.getLogger('')

    @staticmethod
    def print_console(level: int, text: str) -> None:
        the_file.write(f'{Logger.level_to_str(level)}: {text}\n')
        the_file.flush()
        if use_console or level >= Logger.WARN:
            print(f'{Logger.level_to_str(level)}: {text}')

    @staticmethod
    def info(text: str) -> None:
        Logger.print_console(Logger.INFO, text)

    @staticmethod
    def debug(text: str) -> None:
        Logger.print_console(Logger.DEBUG, text)

    @staticmethod
    def warn(text: str) -> None:
        Logger.print_console(Logger.WARN, text)

    @staticmethod
    def error(text: str) -> None:
        Logger.print_console(Logger.ERROR, text)

    @staticmethod
    def to_console(yesno: bool) -> None:
        global use_console
        use_console = yesno

    @staticmethod
    def level_to_str(level: int) -> str:
        return ('DEBUG', 'INFO', 'WARN', 'ERROR', 'FATAL')[level-1]

    @staticmethod
    def init(filename: str='log.txt') -> None:
        global the_file
        the_file = open(filename, 'w')
        Logger.info(f"Logger initialised at {datetime.datetime.now()}")
        

        
