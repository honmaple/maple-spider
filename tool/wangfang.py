#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: wangfang.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-05-15 23:16:30 (CST)
# Last Update:星期五 2017-5-19 10:36:18 (CST)
#          By:
# Description:
# **************************************************************************
from lxml import html
from random import sample
from string import ascii_letters, digits
from time import sleep
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
        path = 'download/{}'.format(self.classify)
        filename = 'download/{}/{}.pdf'.format(self.classify, title)
        if not os.path.exists(path):
            os.mkdir(path)
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
            # logger.info('{} , {}'.format(title, download))
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
            logger.info('{} 下一页: {}'.format(self.classify, next_page))
            response = self.request(next_page)
            return self.parse_list(response)

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
    pool = ThreadPool(20, 2)
    urls = [
        ('马克思',
         'http://210.29.97.21/S/paper.aspx?q=clcnumber%3aA&o=sortby+CitedCount+CoreRank+date+relevance%2fweight%3d5&f=default.clc&n=10&p=103'
         ),
        ('哲学宗教',
         'http://210.29.97.21/S/paper.aspx?q=clcnumber%3aB&o=sortby+CitedCount+CoreRank+date+relevance%2fweight%3d5&f=default.clc&n=10&p=63'
         ),
        ('综合性图书',
         'http://210.29.97.21/S/paper.aspx?q=clcnumber%3aZ&o=sortby+CitedCount+CoreRank+date+relevance%2fweight%3d5&f=default.clc&n=10&p=31'
         ),
        ('自然科学总论',
         'http://210.29.97.21/S/paper.aspx?q=clcnumber%3aN&o=sortby+CitedCount+CoreRank+date+relevance%2fweight%3d5&f=default.clc&n=10&p=47'
         ),
        ('数理科学和化学',
         'http://210.29.97.21/S/paper.aspx?q=clcnumber%3aO&o=sortby+CitedCount+CoreRank+date+relevance%2fweight%3d5&f=default.clc&n=10&p=149'
         ),
        ('天文学地球科学',
         'http://210.29.97.21/S/paper.aspx?q=clcnumber%3aP&o=sortby+CitedCount+CoreRank+date+relevance%2fweight%3d5&f=default.clc&n=10&p=122'
         ),
        ('生物科学',
         'http://210.29.97.21/S/paper.aspx?q=clcnumber%3aQ&o=sortby+CitedCount+CoreRank+date+relevance%2fweight%3d5&f=default.clc&n=10&p=68'
         )
    ]

    def start(url):
        spider = Spider(url[1], url[0])
        spider.start()

    pool.map(start, urls)
