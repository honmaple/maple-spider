#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: douban.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-04-17 10:00:14 (CST)
# Last Update: 2017-05-03 20:14:12
#          By: jianglin
# Description:
# **************************************************************************
from random import randint
from lxml import html
from random import choice
import requests
from agents import AGENTS_ALL
import json
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, Text, Integer
from sqlalchemy.sql import exists
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('postgresql://postgres:password@localhost/spider')
session = sessionmaker(bind=engine)()

# 创建对象的基类:
Base = declarative_base()


class M(Base):
    __tablename__ = 'movie'
    id = Column(Integer, primary_key=True)
    url = Column(String(1024))
    content = Column(Text)

    def __repr__(self):
        return self.url


def gen_bids():
    bids = []
    for i in range(500):
        bid = []
        for x in range(20):
            bid.append(chr(randint(65, 90)))
        bids.append("".join(bid))
    return bids


class Spider(object):
    def __init__(self, start_url):
        self.start_url = start_url
        self.prefix_url = 'https://movie.douban.com'
        self.bid = gen_bids()
        self.cookies = {}

    def request(self, url):
        cookies = {'bid': choice(self.bid)}
        headers = {'User-Agent': choice(AGENTS_ALL)}
        r = requests.get(url, headers=headers, cookies=cookies)
        return r

    def parse_tag(self, response):
        selector = html.fromstring(response.text)
        tags = selector.xpath('//table[@class="tagCol"]//a')
        for tag in tags:
            print(tag.xpath('text()'))
            href = self.prefix_url + tag.xpath('@href')[0]
            self.parse(self.request(href))

    def parse(self, response):
        selector = html.fromstring(response.text)
        movies = selector.xpath('//div[@class="pl2"]/a')
        for movie in movies:
            href = movie.xpath('@href')[0]
            title = movie.xpath('text()')[0].strip()
            description = movie.xpath('span/text()')
            if description:
                description = description[0].strip()
            print('======================={}'.format(response.status_code))
            print('正在爬取:{}{}   href:{}'.format(title, description, href))
            if not session.query(exists().where(M.url == href)).scalar():
                self.parse_content(self.request(href))
        next_page = selector.xpath('//span[@class="next"]/a/@href')
        if next_page:
            return self.parse(self.request(next_page[0]))

    def parse_content(self, response, count=2):
        data = {}
        try:
            selector = html.fromstring(response.text)
            title = selector.xpath('//h1/span[@property="v:itemreviewed"]/text()')
            if not title:
                count -= 1
                if count == 0:
                    return
                return self.parse_content(response, count)
            year = selector.xpath('//h1/span[@class="year"]/text()')
            image = selector.xpath('//a[@class="nbgnbg"]/img/@src')
            summary = selector.xpath('//span[@property="v:summary"]/text()')
            rating_num = selector.xpath('//strong[@class="ll rating_num"]/text()')
            rating_people = selector.xpath(
                '//a[@class="rating_people"]/span/text()')
            stars5 = selector.xpath(
                '//span[@class="stars5 starstop"]/following-sibling::span[1]/text()'
            )
            stars4 = selector.xpath(
                '//span[@class="stars4 starstop"]/following-sibling::span[1]/text()'
            )
            stars3 = selector.xpath(
                '//span[@class="stars3 starstop"]/following-sibling::span[1]/text()'
            )
            stars2 = selector.xpath(
                '//span[@class="stars2 starstop"]/following-sibling::span[1]/text()'
            )
            stars1 = selector.xpath(
                '//span[@class="stars1 starstop"]/following-sibling::span[1]/text()'
            )
            data['title'] = title
            data['year'] = year
            data['image'] = image
            data['summary'] = summary
            data['rating_num'] = rating_num
            data['rating_people'] = rating_people
            data['stars'] = {
                'stars1': stars1,
                'stars2': stars2,
                'stars3': stars3,
                'stars4': stars4,
                'stars5': stars5
            }
            data['info'] = self.info(selector)
            m = M(url=response.url, content=json.dumps(data))
            session.add(m)
            session.commit()
        except Exception:
            pass

    def info(self, selector):
        d = selector.xpath(
            '//div[@id="info"]//span[@class="pl" and contains(text(),"导演")]/following-sibling::span[1]/a/text()'
        )
        b = selector.xpath(
            '//div[@id="info"]//span[@class="pl" and contains(text(),"编剧")]/following-sibling::span[1]/a/text()'
        )
        z = selector.xpath(
            '//div[@id="info"]//span[@class="pl" and contains(text(),"主演")]/following-sibling::span[1]//a/text()'
        )
        l = selector.xpath(
            '//div[@id="info"]//span[@property="v:genre"]/text()')
        g = selector.xpath(
            '//div[@id="info"]//span[@class="pl" and contains(text(),"制片国家/地区:")]/following::text()[1]'
        )
        y = selector.xpath(
            '//div[@id="info"]//span[@class="pl" and contains(text(),"语言:")]/following::text()[1]'
        )
        s = selector.xpath(
            '//div[@id="info"]//span[@property="v:initialReleaseDate"]/text()')
        p = selector.xpath(
            '//div[@id="info"]//span[@property="v:runtime"]/text()')
        i = selector.xpath(
            '//div[@id="info"]//span[@class="pl" and contains(text(),"IMDb链接:")]/following-sibling::a[1]/@href'
        )
        return {
            'd': d,
            'b': b,
            'z': z,
            'l': l,
            'g': g,
            'y': y,
            's': s,
            'p': p,
            'i': i,
        }

    def start(self):
        return self.parse_tag(self.request(self.start_url))


if __name__ == '__main__':
    # Base.metadata.create_all(engine)
    spider = Spider('https://movie.douban.com/tag/')
    spider.start()
