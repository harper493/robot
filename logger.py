#coding:utf-8

from __future__ import annotations
import logging
import datetime
import os

use_console: bool = True
the_file: _io.TextIOWrapper = None    #type: ignore[assignment, name-defined]

class Logger:

    def __init__(self, filename: str='log.txt'):
        try:
            os.remove(filename)
        except:
            pass
        self.my_logger = logging.getLogger('')

    @staticmethod
    def print_console(level: str, text: str) -> None:
        the_file.write(f'{level}: {text}\n')
        the_file.flush()
        if use_console:
            print(f'{level}: {text}')

    @staticmethod
    def info(text: str) -> None:
        Logger.print_console('INFO', text)

    @staticmethod
    def debug(text: str) -> None:
        Logger.print_console('DEBUG', text)

    @staticmethod
    def warn(text: str) -> None:
        Logger.print_console('WARN', text)

    @staticmethod
    def error(text: str) -> None:
        Logger.print_console('ERROR', text)

    @staticmethod
    def to_console(yesno: bool) -> None:
        global use_console
        use_console = yesno

    @staticmethod
    def init(filename: str='log.txt') -> None:
        global the_file
        the_file = open(filename, 'w')
        Logger.info(f"Logger initialised at {datetime.datetime.now()}")
        

        
