#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: ics.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-04-12 16:18:05 (CST)
# Last Update:星期三 2017-4-12 17:4:29 (CST)
#          By:
# Description:
# **************************************************************************
from lxml import html
from random import choice
import requests
import json


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
        hrefs = selector.xpath('//tr')
        datas = []
        for href in hrefs:
            data = {}
            text = href.xpath('td/p[@class="normal"]/text()')
            if len(text) == 6:
                data['name'] = href.xpath('td//p/b/a/text()')[0]
                data['data_types'] = text[0].replace('\xa0', '')
                data['default_task'] = text[1].replace('\xa0', '')
                data['attributes_types'] = text[2].replace('\xa0', '')
                data['instances'] = text[3].replace('\xa0', '')
                data['attributes'] = text[4].replace('\xa0', '')
                data['year'] = text[5].replace('\xa0', '')
            if data:
                datas.append(data)
        a = json.dumps(datas)
        with open('b.json', 'w') as f:
            f.write(a)

    def start(self):
        return self.parse(self.request(self.start_url))


if __name__ == '__main__':
    spider = Spider("http://archive.ics.uci.edu/ml/datasets.html")
    spider.start()
