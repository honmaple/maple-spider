#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: biqu.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-04-25 16:45:12 (CST)
# Last Update:星期二 2017-4-25 22:27:36 (CST)
#          By:
# Description:
# **************************************************************************
from lxml import html
from random import choice
from queue import Queue
import threading
import requests

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Text, Integer, ForeignKey
from sqlalchemy.orm import relationship, backref
from sqlalchemy.sql import exists
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('postgresql://postgres:password@localhost/spider')
session = sessionmaker(bind=engine)()

# 创建对象的基类:
Base = declarative_base()


class BaseMixin(object):
    def __repr__(self):
        return str(self.id)

    def save(self):
        if not self.id:
            session.add(self)
        session.commit()

    def delete(self):
        session.delete(self)
        session.commit()


class Novel(Base, BaseMixin):
    __tablename__ = 'novel'
    id = Column(Integer, primary_key=True)
    url = Column(String(1024))
    title = Column(String(1024))
    category = Column(String(1024))


class NovelContent(Base, BaseMixin):
    __tablename__ = 'novel_chapter'
    id = Column(Integer, primary_key=True)
    chapter = Column(String(1024))
    content = Column(Text)

    novel_id = Column(Integer, ForeignKey('novel.id', ondelete="CASCADE"))
    novel = relationship(
        Novel,
        backref=backref(
            'chapters', cascade='all,delete-orphan', lazy='dynamic'),
        lazy='joined')


class ThreadPool(object):
    '''线程池实现'''

    def __init__(self, num):
        self.num = num
        self.queue = Queue(maxsize=100)
        self.threads = []

    def wait(self):
        self.create_thread()
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
        while not self.queue.empty():
            call, args = self.queue.get()
            call(*args)
            self.queue.task_done()


class Spider(object):
    def __init__(self, start_url):
        self.prefix_url = 'http://m.biqugetw.com'
        self.start_url = start_url

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

    def request(self, url):
        r = requests.get(url, headers=self.headers)
        return r

    def thread(self, url):
        self.parse_index(self.request(url))

    def parse(self, response, **kwargs):
        selector = html.fromstring(response.text)
        categories = selector.xpath('//div[@class="content"]//a')
        for c in categories:
            href = self.prefix_url + c.xpath('@href')[0]
            self.parse_category(self.request(href))
            print(c.xpath('text()'), href)

    def parse_category(self, response, **kwargs):
        selector = html.fromstring(response.text)
        novels = selector.xpath(
            '//div[@class="cover"]/p[@class="line"]/a[@class="blue"]')
        for novel in novels:
            title = novel.xpath('text()')[0]
            href = self.prefix_url + novel.xpath('@href')[0]
            print(novel.xpath('text()'), href)
            pool.add_thread(self.thread, args=(href, ))
            # self.parse_index(self.request(href))
        next_page = selector.xpath('//div[@class="page"]/a[text()="下页"]/@href')
        if next_page:
            href = self.prefix_url + next_page[0]
            response = self.request(href)
            return self.parse_category(response)

    def parse_index(self, response, **kwargs):
        selector = html.fromstring(response.text)
        start_read = selector.xpath('//div[@class="ablum_read"]/span[1]/a')
        href = self.prefix_url + start_read[0].xpath('@href')[0]
        self.parse_table(self.request(href))

    def parse_table(self, response, **kwargs):
        selector = html.fromstring(response.text)
        tables = selector.xpath('//ul[@class="chapter"]/li/a')
        for table in tables:
            title = table.xpath('text()')[0]
            href = self.prefix_url + table.xpath('@href')[0]
            print(title, href)
            self.parse_content(self.request(href))
        next_page = selector.xpath(
            '//div[@class="page"]/a[text()="下一页"]/@href')
        if next_page:
            href = self.prefix_url + next_page[0]
            content = self.request(href)
            return self.parse_table(content)

    def parse_content(self, response, **kwargs):
        selector = html.fromstring(response.text)
        title = selector.xpath('//div[@class="nr_title"]/text()')
        text = selector.xpath('//div[@class="nr_nr"]/div[@id="nr1"]/text()')
        print(text)

    def start(self):
        return self.parse(self.request(self.start_url))


if __name__ == '__main__':
    pool = ThreadPool(1)
    spider = Spider("http://m.biqugetw.com/sort/")
    spider.start()
    pool.wait()
