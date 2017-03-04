#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: spider.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-03-03 15:23:53 (CST)
# Last Update:星期日 2017-3-5 0:13:54 (CST)
#          By:
# Description:
# **************************************************************************
from urllib.request import Request, urlopen
from urllib.error import HTTPError
from bs4 import BeautifulSoup
from queue import Queue
from random import choice
import threading
import click
import logging
import sqlite3
import os
import time


def ProgressBar(itera,
                total,
                prefix='',
                suffix='',
                decimals=0,
                length=100,
                fill='█'):
    percent = ("{0:." + str(decimals) + "f}").format(100 * (itera /
                                                            float(total)))
    filledLength = int(length * itera // total)
    bar = fill * filledLength + '-' * (length - filledLength)
    print('\r%s |%s| %s%% %s' % (prefix, bar, percent, suffix), end='\r')
    # Print New Line on Complete
    if itera == total:
        print()


class showProgress(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.start()

    def run(self):
        _max = 0
        while True:
            _max = max(self.queue.unfinished_tasks, _max)
            i = _max - self.queue.unfinished_tasks + 1
            ProgressBar(
                i,
                _max,
                prefix='爬虫:',
                suffix='(%s/%s)' % (i, _max),
                length=48)
            time.sleep(0.1)
            if self.queue.unfinished_tasks == 0:
                break


class ThreadPool(object):
    '''线程池'''

    def __init__(self, num):
        self.num = num
        self.queue = Queue()
        self.threads = []

    def wait(self):
        self.queue.join()

    def get_thread(self):
        return self.queue.get()

    def add_thread(self, target, args=()):
        self.queue.put((target, args))

    def create_thread(self):
        for t in range(self.num):
            self.threads.append(SpiderThread(self.queue))


class SpiderThread(threading.Thread):
    def __init__(self, queue):
        threading.Thread.__init__(self)
        self.queue = queue
        self.setDaemon(True)
        self.start()

    def run(self):
        # while True:
        #     if self.queue.empty():
        #         if self.i >= 3:
        #             break
        #         self.i += 1
        #         return self.run()
        while not self.queue.empty():
            call, args = self.queue.get(timeout=2)
            url, deep = args
            call(*args)
            self.queue.task_done()


class Sql(object):
    __slots__ = ('db', 'cursor')

    def __init__(self, dbfile):
        # 检测文件名是否合法
        dirname, dbname = os.path.split(dbfile)
        if dirname and dirname != '/tmp':
            raise
        self.db = sqlite3.connect(dbfile, check_same_thread=False)
        self.cursor = self.db.cursor()
        self.create()

    def create(self):
        try:
            self.db.execute('''CREATE TABLE SPIDER
                (ID INT PRIMARY KEY     NOT NULL,
                URL           VARCHAR(512)  NOT NULL,
                KEY           VARCHAR(512)  NOT NULL,
                CONTENT       VARCHAR(1024) NOT NULL);''')
        except sqlite3.OperationalError:
            logger.error('数据库创建错误')

    def insert(self, url, key, content):
        logger.debug('正在插入数据url:%s key:%s content:%s' % (url, key, 's'))
        try:
            self.cursor.execute(
                'INSERT INTO SPIDER(URL,KEY,CONTENT) VALUES(%s, %s, %s)' %
                (url, key, content))
            self.db.commit()
        except sqlite3.OperationalError:
            logging.error('插入 ' + url + ' 数据错误')

    def __exit__(self):
        self.db.close()


class Handle(object):
    def __init__(self, has_key=False, sql=None):
        self.has_key = has_key
        self.sql = sql

    def _no_key(self, url, key, content):
        '''对无关键词页面的处理'''
        pass

    def _has_key(self, url, key, content):
        '''对有关键词页面的处理'''
        self.sql.insert(url, key, content)

    def __call__(self, **kwargs):
        if self.has_key:
            return self._has_key(**kwargs)
        return self._no_key(**kwargs)


class Spider(object):
    def __init__(self, url, deep, key, sql, pool=None):
        self.url = url
        self.deep = deep
        self.key = key
        self.sql = sql
        self.pool = pool
        self.used_urls = set(['http://www.moe.edu.cn/'])
        self.haskey_urls = set()

    @property
    def headers(self):
        '''
        设置header
        '''
        user_agent = [
            'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)',
            "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/532.5 (KHTML, like Gecko) Chrome/4.0.249.0 Safari/532.5",
            "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.27 (KHTML, like Gecko) Chrome/12.0.712.0 Safari/534.27",
            "Mozilla/5.0 (Windows; U; Windows NT 6.0 x64; en-US; rv:1.9pre) Gecko/2008072421 Minefield/3.0.2pre",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:7.0.1) Gecko/20100101 Firefox/7.0.1"
        ]
        return {'User-Agent': choice(user_agent)}

    @property
    def host(self):
        '''
        获取host
        '''
        request = Request(self.url)
        return 'http://' + request.host

    def init(self, url):
        '''初始化爬虫'''
        request = Request(url, headers=self.headers)
        try:
            response = urlopen(request)
            return response.read().decode('utf-8', 'ignore')
        except Exception:
            return ''

    def parse(self, url, deep):
        '''对爬虫内容进行解析'''
        logger.info('当前url: %s' % url)
        logger.info('当前deep: %s' % deep)
        if deep == 0:
            return
        deep -= 1
        has_key = False
        content = self.init(url)
        bp = BeautifulSoup(content, 'lxml')
        if self.key and bp.find(text=self.key):
            has_key = True
            self.haskey_urls.add(url)
        handle = Handle(has_key, self.sql)
        handle(url=url, key=self.key, content=content)
        if deep > 0:
            urls = self.parse_url(bp)
            self.parse_thread(urls, deep)

    def parse_url(self, bp):
        '''找出但前页面所有的a节点'''
        urls = set()
        host = self.host
        for i in bp.find_all('a'):
            _url = i.get('href')
            if _url and not _url.startswith('#') and _url != 'javascript:;':
                if not _url.startswith('http'):
                    _url = host + _url
                urls.add(_url)
        urls = self.used_urls & urls ^ urls
        return urls

    def parse_thread(self, urls, deep):
        for u in urls:
            self.used_urls.add(u)
            self.pool.add_thread(self.parse, args=(u, deep))

    def run(self):
        self.parse(self.url, self.deep)


@click.command()
@click.option(
    '-u', '--url', default='http://www.sina.com.cn/', help='spider start url')
@click.option('-d', '--deep', default=2, help='spider deep')
@click.option('-f', '--logfile', default='spider.log', help='log file name')
@click.option('-l', '--loglevel', default=1, help='log level')
@click.option('-testself', default=1, help='test')
@click.option('-thread', default=10, help='thread pool size')
@click.option('-dbfile', default='spider.db', help='sql file name')
@click.option('-key', default=None, help='spider keywords')
def main(url, deep, logfile, loglevel, testself, thread, dbfile, key):
    global logger, mutex
    logLevel = {
        1: logging.DEBUG,
        2: logging.ERROR,
        3: logging.WARNING,
        4: logging.INFO,
        5: logging.CRITICAL,
    }
    logging.basicConfig(level=logLevel[loglevel])
    logger = logging.getLogger()
    sql = None
    start = time.time()
    if key is not None:
        sql = Sql(dbfile)
    pool = ThreadPool(thread)
    mutex = threading.Lock()
    spider = Spider(url, deep, key, sql, pool)
    spider.run()
    pool.create_thread()
    showProgress(pool.queue)
    pool.wait()
    end = time.time()
    print(end - start)


if __name__ == '__main__':
    main()
