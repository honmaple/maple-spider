#!/usr/bin/env python
# -*- coding: utf-8 -*-
# **************************************************************************
# Copyright © 2017 jianglin
# File Name: spider.py
# Author: jianglin
# Email: xiyang0807@gmail.com
# Created: 2017-04-17 10:09:17 (CST)
# Last Update:星期六 2017-9-23 11:47:0 (CST)
#          By:
# Description:
# **************************************************************************
from datetime import datetime
from random import choice, sample
from string import ascii_letters, digits

import requests
from requests import Response
from requests.exceptions import (ConnectionError, HTTPError, RequestException,
                                 Timeout)
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import types

from lxml import html

from .agents import AGENTS_ALL


class SpiderMixin(object):
    def __init__(self, start_url, prefix_url=''):
        self.start_url = start_url
        self.prefix_url = prefix_url

    def retry_request(self, r, url, count):
        if count == 0:
            return r
        count -= 1
        return self.request(url, count)

    def request(self, url, count=3, **kwargs):
        headers = {'User-Agent': choice(AGENTS_ALL)}
        kwargs.update(headers=headers)
        kwargs.update(timeout=10)
        try:
            r = requests.get(url, **kwargs)
        except Timeout as e:
            # 超时
            print('超时: {} {}'.format(url, e))
            return self.retry_request(r, url, count)
        except HTTPError as e:
            # 请求失败
            print('请求失败: {} {}'.format(url, e))
            return self.retry_request(r, url, count)
        except RequestException as e:
            print('其他错误: {} {}'.format(url, e))
            return self.retry_request(r, url, count)
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


class SpiderSQL(object):
    Base = declarative_base()

    def __init__(self, sql):
        self.engine = create_engine(sql)
        self.session = sessionmaker(bind=self.engine)()

    def create(self, tablename=None):
        self.Base.metadata.create_all(self.engine)

    def insert(self, **values):
        pass

    def delete(self, value_id):
        pass

    def table(self):
        pass


# class SpiderItem(types):
#     pass
