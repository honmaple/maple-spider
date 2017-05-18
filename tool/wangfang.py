#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: wangfang.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-05-15 23:16:30 (CST)
# Last Update:星期四 2017-5-18 16:12:59 (CST)
#          By:
# Description:
# **************************************************************************
from lxml import html
from random import sample
from string import ascii_letters, digits
import os
import sys
sys.path.append('..')

from common.pool import ThreadPool
from common.log import log
from common.spider import SpiderMixin

logger = log('spider.log')


class Spider(SpiderMixin):
    def __init__(self, start_url, classify):
        self.start_url = start_url
        self.classify = classify
        self.prefix_url = 'http://210.29.97.21'

    def thread(self, href, title):
        filename = 'download/{}/{}.pdf'.format(self.classify, title)
        if not os.path.exists(filename):
            self.parse_download(self.request(href), title=title)

    def parse_list(self, response):
        selector = html.fromstring(response.text)
        lists = selector.xpath('//ul[@class="list_ul"]')
        for l in lists:
            title = l.xpath('li[@class="title_li"]/a/text()')
            download = l.xpath(
                'li[@class="zi"]/span[@style="visibility:visible"]/a[@title="下载全文"]/@href'
            )
            logger.info('{} , {}'.format(title, download))
            if download:
                href = self.prefix_url + download[0]
                title = title[0].replace('/', '-')
                # thr = Thread(target=self.thread, args=(href, title))
                # thr.start()
                pool.add_thread(self.thread, args=(href, title))
                # self.parse_download(self.request(href), title=title[0])
        next_page = selector.xpath(
            '//p[@class="pager_space"]/a[@class="page" and contains(text(),"下一页")]/@href'
        )
        if next_page:
            next_page = next_page[0]
            logger.info(next_page)
            return self.parse_list(self.request(next_page))

    def parse_download(self, response, **kwargs):
        title = kwargs.get('title')
        if not title:
            title = ''.join(sample(ascii_letters + digits, 16))
        filename = 'download/{}/{}.pdf'.format(self.classify, title)
        logger.info('正在下载: {}'.format(title))
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=512):
                if chunk:
                    f.write(chunk)

    def start(self):
        return self.parse_list(self.request(self.start_url))


if __name__ == '__main__':
    pool = ThreadPool(10, 2)
    url = 'http://210.29.97.21/S/paper.aspx?q=clcnumber%3aA&o=sortby+CitedCount+CoreRank+date+relevance%2fweight%3d5&f=default.clc&n=10&p=38'
    pool.add_process(Spider(url, 'makesi').start())
    url = 'http://210.29.97.21/S/paper.aspx?q=clcnumber%3aB&o=sortby+CitedCount+CoreRank+date+relevance%2fweight%3d5&f=default.clc&n=10&p=38'
    pool.add_process(Spider(url, 'zhexue').start())
