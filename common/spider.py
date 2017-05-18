#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: spider.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-04-17 10:09:17 (CST)
# Last Update:星期四 2017-5-18 16:1:47 (CST)
#          By:
# Description:
# **************************************************************************
from lxml import html
from random import choice, sample
from string import ascii_letters, digits

import requests

from .agents import AGENTS_ALL


class SpiderMixin(object):
    def __init__(self, start_url, prefix_url=''):
        self.start_url = start_url
        self.prefix_url = prefix_url

    def request(self, url, **kwargs):
        headers = {'User-Agent': choice(AGENTS_ALL)}
        kwargs.update(headers=headers)
        r = requests.get(url, **kwargs)
        return r

    def parse(self, response, **kwargs):
        pass

    def parse_download(self, response, **kwargs):
        filename = kwargs.pop('filename', None)
        if not filename:
            filename = ''.join(sample(ascii_letters + digits, 16))
        chunk_size = kwargs.pop('chunk_size', 512)
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=chunk_size):
                if chunk:
                    f.write(chunk)

    def selector(self, response):
        return html.fromstring(response.text)

    def start(self):
        response = self.request(self.start_url)
        return self.parse(response)
