#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: log.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-05-18 15:53:45 (CST)
# Last Update:星期四 2017-5-18 16:10:53 (CST)
#          By:
# Description:
# **************************************************************************
import logging
import sys
from logging import FileHandler, StreamHandler, Formatter

# DEFAULT_FORMATTER = '%(asctime)s %(levelname)s %(message)s'
DEFAULT_FORMATTER = '%(levelname)s %(message)s'


def log(filename='', formatter=DEFAULT_FORMATTER):
    log_console = StreamHandler(sys.stderr)
    log_console.setFormatter(Formatter(formatter))
    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(log_console)
    if filename:
        log_file = FileHandler(filename)
        logger.addHandler(log_file)
    return logger
