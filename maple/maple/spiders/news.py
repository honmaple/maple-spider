#!/usr/bin/env python
# -*- coding=UTF-8 -*-
#*************************************************************************
# Copyright © 2015 JiangLin. All rights reserved.
# File Name: news.py
# Author:JiangLin
# Mail:xiyang0807@gmail.com
# Created Time: 2016-04-03 23:02:32
# Last Update: 2016-04-04 17:43:50
#          By: jianglin
# Description: 爬取学校新闻
#*************************************************************************
import scrapy
from maple.items import NewsItem,BsNewsItem
from scrapy.http import Request
from datetime import datetime


class NewsSpider(scrapy.spiders.Spider):
    name = "news"
    allowed_domains = ["202.119.112.75"]
    start_urls = []
    for page in range(1, 190):
        url = 'http://202.119.112.75/s/2001/t/2016/p/5/i/%d/list.htm' % page
        start_urls.append(url)

    def parse_item(self, response):
        p1 = response.xpath('//td[contains(@class, "content")]/p')
        p2 = response.xpath('//td[contains(@class, "content")]/div')
        p = p1 or p2
        item = response.meta['item']
        content = ''
        for text in p:
            c = text.xpath('*/text()').extract()
            if len(c) >= 1:
                con = c[0] + '\n'
                content += con
        item['content'] = content
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
            yield Request(item['url'],
                          meta={'item': item},
                          callback=self.parse_item)

class BsSpider(scrapy.spiders.Spider):
    name = "bsnews"
    allowed_domains = ["bs.hhuc.edu.cn"]
    start_urls = []
    for page in range(1, 2):
        url = 'http://bs.hhuc.edu.cn/s/2039/t/2371/p/3/i/%d/list.htm' % page
        start_urls.append(url)

    def parse_item(self, response):
        p1 = response.xpath('//td[contains(@class, "content")]/p')
        p2 = response.xpath('//td[contains(@class, "content")]/div')
        p = p1 or p2
        item = response.meta['item']
        content = ''
        for text in p:
            c = text.xpath('*/text()').extract()
            if len(c) >= 1:
                con = c[0] + '\n'
                content += con
        item['content'] = content
        return item

    def parse(self, response):
        sites = response.xpath('//table[contains(@class, "columnStyle")]/tr')
        items = []
        for site in sites:
            item = BsNewsItem()
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
            yield Request(item['url'],
                          meta={'item': item},
                          callback=self.parse_item)
