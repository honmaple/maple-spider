#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: netease_music.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-05-18 16:26:02 (CST)
# Last Update:星期五 2017-5-19 19:13:30 (CST)
#          By:
# Description:
# **************************************************************************
import sys
import requests
from random import choice
import re

sys.path.append('..')

from common.pool import ThreadPool
from common.log import log
from common.spider import SpiderMixin
from common.agents import AGENTS_ALL

headers = {
    'Accept': '*/*',
    'Accept-Encoding': 'gzip,deflate,sdch',
    'Accept-Language': 'zh-CN,zh;q=0.8',
    'Connection': 'keep-alive',
    'Content-Type': 'application/x-www-form-urlencoded',
    'Host': 'music.163.com',
    'Referer': 'http://music.163.com/search/',
    'User-Agent': choice(AGENTS_ALL)
}

cookies = {'appver': '1.5.2'}


class Spider(SpiderMixin):
    def request(self, url, count=3):
        r = requests.get(url, headers=headers, cookies=cookies)
        return r

    def parse(self, response):
        selector = self.selector(response)
        playlist = selector.xpath('//a[@class="tit f-thide s-fc0"]')
        for play in playlist:
            title = play.xpath('text()')[0]
            href = play.xpath('@href')[0]
            playlist_id = href.split('?id=')[1]
            print(title, playlist_id)
            href = 'http://music.163.com/api/playlist/detail?id={}'.format(
                playlist_id)
            response = self.request(href)
            self.parse_play(response)

    def parse_play(self, response):
        play = response.json()['result']['tracks']
        for i in play:
            name = i['name'].replace('\xa0', ' ').replace('/', ' ')
            print(name, i['id'])
            href = 'http://music.163.com/api/song/lyric?os=osx&id={}&lv=-1&kv=-1&tv=-1'.format(
                i['id'])
            response = self.request(href)
            self.parse_lyric(response, name=name)

    def parse_lyric(self, response, **kwargs):
        name = kwargs['name']
        lyric = response.json()
        lyric_info = ''
        if 'lrc' in lyric and 'lyric' in lyric['lrc']:
            lyric_info = lyric['lrc']['lyric']
        if lyric_info:
            with open('lyric/1/{}.lrc'.format(name), 'w') as f:
                f.write(lyric_info)

    def save_lyric(self, lyric):
        lyric = re.sub(r'\[.*\]', '', lyric)
        print(lyric)


if __name__ == '__main__':
    for i in range(0, 42):
        spider = Spider(
            'http://music.163.com/discover/playlist/?order=hot&cat=%E5%8F%A4%E9%A3%8E&limit=35&offset={}'.
            format(i * 35))
        spider.start()
