#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: spider.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-03-03 15:23:53 (CST)
# Last Update:星期日 2017-3-5 20:3:1 (CST)
#          By: jianglin
# Description: a spider.usage: python spider.py --help
# **************************************************************************
from urllib.request import Request, urlopen
from urllib.parse import urlparse
from urllib.error import HTTPError, URLError
from socket import timeout
from bs4 import BeautifulSoup
from queue import Queue
from random import choice
import threading
import click
import logging
import sqlite3
import os
import time
import pickle


def ProgressBar(itera,
                total,
                prefix='',
                suffix='',
                decimals=0,
                length=100,
                fill='█'):
    if total > 0:
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
        while not self.queue.empty():
            _max = max(self.queue.unfinished_tasks, _max)
            i = _max - self.queue.unfinished_tasks
            ProgressBar(
                i, _max, prefix='爬虫:', suffix='(%s/%s)' % (i, _max), length=48)
            time.sleep(10)


class ThreadPool(object):
    '''线程池实现'''

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
        # 重启线程
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
        # 检测文件名是否合法,只允许当前目录及tmp
        dirname, dbname = os.path.split(dbfile)
        if dirname and dirname != '/tmp':
            raise ValueError
        self.db = sqlite3.connect(dbfile, check_same_thread=False)
        self.cursor = self.db.cursor()
        self.create()

    def create(self):
        logger.debug('正在创建数据表spider')
        try:
            self.db.execute('''CREATE TABLE IF NOT EXISTS SPIDER (
                 ID INTEGER PRIMARY KEY  AUTOINCREMENT,
                 URL           VARCHAR(512)  NOT NULL,
                 KEY           VARCHAR(512)  NOT NULL,
                 CONTENT       TEXT NOT NULL);''')
        except sqlite3.OperationalError:
            logger.error('数据库创建错误')

    def insert(self, url, key, content):
        logger.debug('正在插入数据url:%s key:%s' % (url, key))
        key = ','.join(key)
        content = pickle.dumps(content)
        if not self.select(url, key):
            try:
                self.cursor.execute(
                    "INSERT INTO SPIDER (URL,KEY,CONTENT) VALUES (?, ?, ?)",
                    (url, key, content))
                self.db.commit()
            except (sqlite3.OperationalError):
                logging.error('插入 ' + url + ' 数据错误')

    def select(self, url, key):
        c = self.cursor.execute(
            "SELECT ID FROM SPIDER WHERE URL=? AND KEY = ?", (url, key))
        return c.fetchone()


class Handle(object):
    def __init__(self, has_key=False, sql=None):
        self.has_key = has_key
        self.sql = sql

    def _no_key(self, url, key, content):
        '''
        对无关键词页面的处理:下载到本地
        对于爬虫可能需要判断文件是否存在
        '''
        url = urlparse(url)
        key = ','.join(key)
        path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'download',
            url.netloc.replace('.', '-'))
        if not os.path.exists(path):
            os.makedirs(path)
        name = url.netloc + url.path
        file = os.path.join(path, name.replace('/', '-') + '.html')
        if not os.path.exists(file):
            with open(file, 'w+') as f:
                f.write(content)

    def _has_key(self, url, key, content):
        '''对有关键词页面的处理:保存到数据库'''
        with self.sql.db:
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
        url = urlparse(self.url)
        return 'http://' + url.netloc
        # request = Request(self.url)
        # return 'http://' + request.host

    def init(self, url):
        '''初始化爬虫'''
        self.used_urls.add(url)
        request = Request(url, headers=self.headers)
        try:
            response = urlopen(request, timeout=10)
            return response.read()
        except (HTTPError, URLError) as e:
            logger.error('爬取失败%s ,原因:%s' % (url, e.reason))
            return ''
        except timeout:
            logger.error('爬取失败:%s ,原因:timeout' % url)
            return ''
        except Exception as e:
            logger.error('爬取失败%s ,原因:%s' % (url, e))
            return ''

    def parse(self, url, deep):
        '''对爬虫内容进行解析'''
        logger.info('正在抓取url: %s deep:%s' % (url, self.deep - deep + 1))
        if deep == 0:
            return
        deep -= 1
        has_key = False
        content = self.init(url)
        try:
            content = content.decode('gbk')
        except UnicodeDecodeError:
            content = content.decode('utf-8', 'ignore')
        except AttributeError:
            content = content
        bp = BeautifulSoup(content, 'lxml')
        # if self.key and self.key in content:
        if self.key and bp.find(text=self.key):
            has_key = True
            self.haskey_urls.add(url)
        lock.acquire()
        handle = Handle(has_key, self.sql)
        handle(url=url, key=self.key, content=content)
        lock.release()
        if deep > 0:
            urls = self.parse_url(bp)
            self.parse_thread(urls, deep)

    def parse_url(self, bp):
        '''找出但前页面所有的a节点'''
        urls = set()
        host = self.host
        exclude_urls = ['javascript:;', 'javascript:void 0;']
        for i in bp.find_all('a'):
            _url = i.get('href')
            # 忽略单页应用及javascript操作的href
            if _url and not _url.startswith('#') and _url not in exclude_urls:
                if not _url.startswith('http'):
                    _url = host + _url
                    self.url = _url
                urls.add(_url)
        urls = self.used_urls & urls ^ urls
        return urls

    def parse_thread(self, urls, deep):
        '''增加至队列'''
        for u in urls:
            self.pool.add_thread(self.parse, args=(u, deep))

    def run(self):
        self.parse(self.url, self.deep)


@click.command()
@click.option(
    '-u', '--url', default='http://www.sina.com.cn/', help='spider start url')
@click.option('-d', '--deep', default=2, help='spider deep')
@click.option('-f', '--logfile', default='spider.log', help='log file name')
@click.option('-l', '--loglevel', default=5, help='log level')
@click.option('-t', '--thread', default=10, help='thread pool size')
@click.option('-k', '--key', default=None, help='spider keywords')
@click.option('--dbfile', default='spider.db', help='sql file name')
@click.option('--testself', default=False, help='test')
def main(url, deep, logfile, loglevel, testself, thread, dbfile, key):
    global logger, lock
    logLevel = {
        1: logging.CRITICAL,
        2: logging.ERROR,
        3: logging.WARNING,
        4: logging.INFO,
        5: logging.DEBUG
    }
    logging.basicConfig(filename=logfile, level=logLevel[loglevel])
    logger = logging.getLogger()
    sql = None
    if key is not None:
        sql = Sql(dbfile)
        key = key.split(',')
    pool = ThreadPool(thread)
    lock = threading.Lock()
    spider = Spider(url, deep, key, sql, pool)
    spider.run()
    pool.create_thread()
    showProgress(pool.queue)
    pool.wait()


if __name__ == '__main__':
    main()
