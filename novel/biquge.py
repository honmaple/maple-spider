#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: biquge.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-04-04 16:58:39 (CST)
# Last Update:星期二 2017-4-4 18:25:39 (CST)
#          By:
# Description:
# **************************************************************************
from bs4 import BeautifulSoup
from lxml import html
import requests
from random import choice


class Spider(object):
    def __init__(self, start_url):
        self.url_prefix = 'http://m.biqugetw.com'
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
        return r.text

    def parse(self, content):
        selector = html.fromstring(content)
        hrefs = selector.xpath('//ul[@class="chapter"]/li/a')
        for href in hrefs:
            title = href.xpath('text()')[0]
            url = self.url_prefix + href.xpath('@href')[0]
            print(title, url)
            self.parse_content(title, self.request(url))
        next_page = selector.xpath(
            '//div[@class="page"]/a[text()="下一页"]/@href')
        if next_page:
            url = self.url_prefix + next_page[0]
            content = self.request(url)
            return self.parse(content)
        return

    def parse_content(self, title, content):
        selector = html.fromstring(content)
        text = selector.xpath('//div[@class="nr_nr"]/div[@id="nr1"]/text()')
        text = '\n'.join(text)
        with open('1.txt', 'a') as f:
            text = text.replace('\xa0', ' ')
            f.writelines('\n\n{}\n\n{}'.format(title, text))

    def start(self):
        return self.parse(self.request(self.start_url))


if __name__ == '__main__':
    spider = Spider("http://m.biqugetw.com/4/4571/")
    spider.start()
