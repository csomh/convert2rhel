# -*- coding: utf-8 -*-
#
# Copyright(C) 2016 Red Hat, Inc.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
'''
Customized logging functionality

CRITICAL  (50)    Calls critical() function and sys.exit(1)
ERROR     (40)    Prints error message using date/time
WARNING   (30)    Prints warning message using date/time
INFO      (20)    Prints info message (no date/time, just plain message)
TASK      (15)    CUSTOM LABEL - Prints a task header message (using asterisks)
DEBUG     (10)    Prints debug message (using date/time)
FILE      (5)     CUSTOM LABEL - Prints only to file handler (using date/time)
'''
import logging
import sys
import os

LOG_DIR = "/var/log/convert2rhel"

class LOG_LEVEL_TASK:
    level = 15
    label = "TASK"


class LOG_LEVEL_FILE:
    level = 5
    label = "FILE"


def initialize_logger(log_name):
    '''Initialize custom logging levels, handlers, and so on. Call this method
    from your application's main start point.
        log_name = the name for the log file
    '''
    # check if already initialized with custom class
    if logging.getLoggerClass() == CustomLogger:
        return
    # set custom class
    logging.setLoggerClass(CustomLogger)
    # set custom labels
    logging.addLevelName(LOG_LEVEL_TASK.level, LOG_LEVEL_TASK.label)
    logging.addLevelName(LOG_LEVEL_FILE.level, LOG_LEVEL_FILE.label)
    # enable raising exceptions
    logging.raiseExceptions = True
    # get root logger
    logger = logging.getLogger("convert2rhel")
    # propagate
    logger.propagate = False
    # set default logging level
    logger.setLevel(LOG_LEVEL_FILE.level)

    # create sys.stdout handler for info/debug
    stdout_handler = logging.StreamHandler(sys.stdout)
    formatter = CustomFormatter("%(message)s")
    stdout_handler.setFormatter(formatter)
    stdout_handler.setLevel(logging.DEBUG)
    logger.addHandler(stdout_handler)

    # create file handler
    if not os.path.isdir(LOG_DIR):
        os.makedirs(LOG_DIR)
    handler = logging.FileHandler(os.path.join(LOG_DIR, log_name), "w")
    formatter = CustomFormatter("%(message)s")
    handler.setFormatter(formatter)
    handler.setLevel(LOG_LEVEL_FILE.level)
    logger.addHandler(handler)


class CustomLogger(logging.Logger, object):
    """Customized Logger class

    Python 2.6 workaround - logging.Formatter class does not use new-style
        class and causes 'TypeError: super() argument 1 must be type, not
        classobj' so we use multiple inheritance to get around the problem.
    """
    def task(self, msg, *args, **kwargs):
        super(CustomLogger, self).log(LOG_LEVEL_TASK.level, msg, *args,
                                      **kwargs)

    def file(self, msg, *args, **kwargs):
        super(CustomLogger, self).log(LOG_LEVEL_FILE.level, msg, *args,
                                      **kwargs)

    def critical(self, msg, *args, **kwargs):
        super(CustomLogger, self).critical(msg, *args, **kwargs)
        sys.exit(1)

    def debug(self, msg, *args, **kwargs):
        from convert2rhel.toolopts import tool_opts
        if tool_opts.debug:
            super(CustomLogger, self).debug(msg, *args, **kwargs)
        else:
            pass

    def info(self, msg, *args, **kwargs):
        super(CustomLogger, self).info(msg, *args, **kwargs)


class CustomFormatter(logging.Formatter, object):
    """Custom formatter to handle different logging formats based on logging level

    Python 2.6 workaround - logging.Formatter class does not use new-style
        class and causes 'TypeError: super() argument 1 must be type, not
        classobj' so we use multiple inheritance to get around the problem.
    """
    def format(self, record):
        if record.levelno == LOG_LEVEL_TASK.level:
            temp = '*' * (90 - len(record.msg) - 25)
            self._fmt = "\n[%(asctime)s] %(levelname)s - [%(message)s] " + temp
            self.datefmt = "%m/%d/%Y %H:%M:%S"
        elif record.levelno in [logging.INFO, LOG_LEVEL_FILE.level]:
            self._fmt = "%(message)s"
            self.datefmt = ""
        elif record.levelno in [logging.WARNING]:
            self._fmt = "%(levelname)s - %(message)s"
            self.datefmt = ""
        else:
            self._fmt = "[%(asctime)s] %(levelname)s - %(message)s"
            self.datefmt = "%m/%d/%Y %H:%M:%S"

        return super(CustomFormatter, self).format(record)
