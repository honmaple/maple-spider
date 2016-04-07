#!/usr/bin/env python
# -*- coding=UTF-8 -*-
#*************************************************************************
# Copyright © 2015 JiangLin. All rights reserved.
# File Name: news.py
# Author:JiangLin
# Mail:xiyang0807@gmail.com
# Created Time: 2016-04-03 23:02:32
# Last Update: 星期四 2016-4-7 12:57:8 (CST)
#          By: jianglin
# Description: 爬取学校新闻
#*************************************************************************
import scrapy
from maple.items import NewsItem
from scrapy.http import Request
from scrapy.selector import Selector
from datetime import datetime
from maple.models import News, DBSession

session = DBSession()


def exsit_session(url):
    a = session.query(News.url).filter_by(url=url).first()
    if not a:
        return False
    else:
        return True


class NewsSpider(scrapy.spiders.Spider):
    name = "news"
    allowed_domains = ["202.119.112.75"]
    start_urls = []
    for page in range(1, 3):
        url = 'http://202.119.112.75/s/2001/t/2016/p/5/i/%d/list.htm' % page
        start_urls.append(url)

    def parse_item(self, response):
        p1 = response.xpath('//td[contains(@class, "content")]/p')
        p2 = response.xpath('//td[contains(@class, "content")]/div')
        p = p1 or p2
        item = response.meta['item']
        content = ''
        for text in p:
            c1 = text.xpath('text()').extract()
            c2 = text.xpath('*/text()').extract()
            c3 = text.xpath('*/*/text()').extract()
            c4 = text.xpath('*/*/*/text()').extract()
            c = c1 + c2 + c3 + c4
            for i in c:
                con = i + '\n'
                content += con
        item['content'] = content
        item['category'] = 'hhuc'
        return item

    def parse(self, response):
        sites = response.xpath('//table[contains(@class, "columnStyle")]/tr')
        items = []
        for site in sites:
            item = NewsItem()
            title = site.xpath('td[1]/a/font/text()').extract()
            url = site.xpath('td[1]/a/@href').extract()
            time = site.xpath('td[2]/text()').extract()
            if len(title) == 1:
                item['title'] = title[0]
            if len(url) == 1:
                item['url'] = 'http://202.119.112.75' + url[0]
            if len(time) == 1:
                date_time = datetime.strptime(time[0], '%Y-%m-%d')
                item['time'] = date_time
            items.append(item)
        for item in items:
            if not exsit_session(item['url']):
                yield Request(item['url'],
                            meta={'item': item},
                            callback=self.parse_item)


class BsSpider(scrapy.spiders.Spider):
    name = "bs"
    allowed_domains = ["bs.hhuc.edu.cn"]
    start_urls = []
    for page in range(1, 3):
        url = 'http://bs.hhuc.edu.cn/s/2039/t/2371/p/3/i/%d/list.htm' % page
        start_urls.append(url)

    def parse_item(self, response):
        p1 = response.xpath('//td[contains(@class, "content")]/p')
        p2 = response.xpath('//td[contains(@class, "content")]/div')
        p = p1 or p2
        item = response.meta['item']
        content = ''
        for text in p:
            c1 = text.xpath('text()').extract()
            c2 = text.xpath('*/text()').extract()
            c3 = text.xpath('*/*/text()').extract()
            c4 = text.xpath('*/*/*/text()').extract()
            c = c1 + c2 + c3 + c4
            for i in c:
                con = i + '\n'
                content += con
        item['content'] = content
        item['category'] = 'bs'
        return item

    def parse(self, response):
        sites = response.xpath('//table[contains(@class, "columnStyle")]/tr')
        items = []
        for site in sites:
            item = NewsItem()
            title = site.xpath('td[1]/a/font/text()').extract()
            url = site.xpath('td[1]/a/@href').extract()
            time = site.xpath('td[2]/text()').extract()
            if len(title) == 1:
                item['title'] = title[0]
            if len(url) == 1:
                item['url'] = 'http://bs.hhuc.edu.cn' + url[0]
            if len(time) == 1:
                date_time = datetime.strptime(time[0], '%Y-%m-%d')
                item['time'] = date_time
            items.append(item)
        for item in items:
            if not exsit_session(item['url']):
                yield Request(item['url'],
                            meta={'item': item},
                            callback=self.parse_item)


class WulwxySpider(scrapy.spiders.Spider):
    name = "wulwxy"
    allowed_domains = ["wulwxy.hhuc.edu.cn"]
    start_urls = []
    for page in range(1, 3):
        url = 'http://wulwxy.hhuc.edu.cn/s/2059/t/2561/p/4/i/%d/list.htm' % page
        start_urls.append(url)

    def parse_item(self, response):
        p1 = response.xpath('//td[contains(@height, "400")]/p')
        p2 = response.xpath('//td[contains(@height, "400")]/div')
        p = p1 or p2
        item = response.meta['item']
        content = ''
        for text in p:
            c1 = text.xpath('text()').extract()
            c2 = text.xpath('*/text()').extract()
            c3 = text.xpath('*/*/text()').extract()
            c4 = text.xpath('*/*/*/text()').extract()
            c = c1 + c2 + c3 + c4
            for i in c:
                content += i
        print(content)
        item['content'] = content
        item['category'] = 'wulwxy'
        return item

    def parse(self, response):
        sites = response.xpath('//table[contains(@class, "columnStyle")]/tr')
        items = []
        for site in sites:
            item = NewsItem()
            title = site.xpath('td[1]/a/font/text()').extract()
            url = site.xpath('td[1]/a/@href').extract()
            time = site.xpath('td[2]/text()').extract()
            if len(title) == 1:
                item['title'] = title[0]
            if len(url) == 1:
                item['url'] = 'http://wulwxy.hhuc.edu.cn' + url[0]
            if len(time) == 1:
                date_time = datetime.strptime(time[0], '%Y-%m-%d')
                item['time'] = date_time
            items.append(item)
        for item in items:
            if not exsit_session(item['url']):
                yield Request(item['url'],
                            meta={'item': item},
                            callback=self.parse_item)


class JidianSpider(scrapy.spiders.Spider):
    name = "jidian"
    allowed_domains = ["jidian.hhuc.edu.cn"]
    start_urls = []
    for page in range(1, 3):
        url = 'http://jidian.hhuc.edu.cn/s/2029/t/2608/p/3/i/%d/list.htm' % page
        start_urls.append(url)

    def parse_item(self, response):
        try:
            p1 = response.xpath('//table[contains(@width, "98%")]\
                                /tr/td[contains(@valign,"top")]/p')
            p2 = response.xpath('//table[contains(@width, "98%")]\
                                /tr/td[contains(@valign,"top")]/div')
        except:
            hxs = Selector(text=response.body)
            p1 = hxs.xpath('//table[contains(@width, "98%")]\
                                /tr/td[contains(@valign,"top")]/p')
            p2 = hxs.xpath('//table[contains(@width, "98%")]\
                                /tr/td[contains(@valign,"top")]/div')
        p = p1 or p2
        item = response.meta['item']
        content = ''
        for text in p:
            c1 = text.xpath('text()').extract()
            c2 = text.xpath('*/text()').extract()
            c3 = text.xpath('*/*/text()').extract()
            c4 = text.xpath('*/*/*/text()').extract()
            c = c1 + c2 + c3 + c4
            for i in c:
                con = i + '\n'
                content += con
        print(content)
        item['content'] = content
        item['category'] = 'jidian'
        return item

    def parse(self, response):
        sites = response.xpath('//table[contains(@class, "columnStyle")]/tr')
        items = []
        for site in sites:
            item = NewsItem()
            title = site.xpath('td[1]/a/font/text()').extract()
            url = site.xpath('td[1]/a/@href').extract()
            time = site.xpath('td[2]/text()').extract()
            if len(title) == 1:
                item['title'] = title[0]
            if len(url) == 1:
                item['url'] = 'http://jidian.hhuc.edu.cn' + url[0]
            if len(time) == 1:
                date_time = datetime.strptime(time[0], '%Y-%m-%d')
                item['time'] = date_time
            items.append(item)
        for item in items:
            if not exsit_session(item['url']):
                yield Request(item['url'],
                            meta={'item': item},
                            callback=self.parse_item)
