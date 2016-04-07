#!/usr/bin/env python
# -*- coding=UTF-8 -*-
#*************************************************************************
# Copyright © 2015 JiangLin. All rights reserved.
# File Name: user_agent.py
# Author:JiangLin
# Mail:xiyang0807@gmail.com
# Created Time: 2016-04-04 19:14:39
# Last Update: 2016-04-04 20:19:05
#          By: jianglin
# Description:
#*************************************************************************
import random
from maple.settings import USER_AGENTS
from scrapy.contrib.downloadermiddleware.useragent import UserAgentMiddleware


class RotateUserAgentMiddleware(UserAgentMiddleware):

    def __init__(self, user_agent=''):
        self.user_agent = user_agent

    def process_request(self, request, spider):
        ua = random.choice(USER_AGENTS)
        if ua:
            request.headers.setdefault('User-Agent', ua)


#  class ProxyMiddleware(object):

    #  def __init__(self, settings):
        #  self.proxy_list = settings.get('PROXY_LIST')
        #  with open(self.proxy_list) as f:
            #  self.proxies = [ip.strip() for ip in f]

    #  def parse_request(self, request, spider):
        #  request.meta['proxy'] = 'http://{}'.format(random.choice(self.proxies))
