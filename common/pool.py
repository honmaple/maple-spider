#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: pool.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-05-18 14:11:28 (CST)
# Last Update:星期五 2017-5-19 1:53:41 (CST)
#          By:
# Description:
# **************************************************************************
from concurrent.futures import wait as thread_wait
from concurrent.futures import (ProcessPoolExecutor, ThreadPoolExecutor,
                                as_completed)
from queue import Queue
from threading import Thread
from concurrent.futures.thread import _worker, weakref, _threads_queues


class _ThreadPoolExecutor(ThreadPoolExecutor):
    def _adjust_thread_count(self):
        def weakref_cb(_, q=self._work_queue):
            q.put(None)

        num_threads = len(self._threads)
        if num_threads < self._max_workers:
            thread_name = '%s_%d' % (self._thread_name_prefix or self,
                                     num_threads)
            t = Thread(
                name=thread_name,
                target=_worker,
                args=(weakref.ref(self, weakref_cb), self._work_queue))
            # t.daemon = True
            t.start()
            self._threads.add(t)
            _threads_queues[t] = self._work_queue


class ThreadPool(object):
    '''线程池实现'''

    def __init__(self, thread_num=1, process_num=1, q_size=2000):
        self.thread_pool = _ThreadPoolExecutor(thread_num)
        self.process_pool = ProcessPoolExecutor(process_num)
        self.result_queue = Queue(q_size)
        self.threads = []

    def wait(self):
        thread_wait(self.threads)

    def add_thread(self, target, args=()):
        result = self.thread_pool.submit(target, *args)
        # self.result_queue.put(result)

    def add_process(self, target, args=()):
        self.process_pool.submit(target, *args)

    def map(self, target, urls=[]):
        self.process_pool.map(target, urls)
