#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: pool.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-05-18 14:11:28 (CST)
# Last Update:星期四 2017-5-18 15:6:6 (CST)
#          By:
# Description:
# **************************************************************************
from concurrent.futures import wait as thread_wait
from concurrent.futures import (ProcessPoolExecutor, ThreadPoolExecutor,
                                as_completed)
from queue import Queue
from threading import Thread


class ThreadPool(object):
    '''线程池实现'''

    def __init__(self, thread_num=1, process_num=1, q_size=2000):
        self.thread_pool = ThreadPoolExecutor(thread_num)
        self.process_pool = ProcessPoolExecutor(process_num)
        self.result_queue = Queue(q_size)
        self.threads = []

    def wait(self):
        thread_wait(self.threads)

    def add_thread(self, target, args=()):
        result = self.thread_pool.submit(target, *args)
        self.result_queue.put(result)

    def add_process(self, target, args=()):
        self.process_pool.submit(target, *args)
