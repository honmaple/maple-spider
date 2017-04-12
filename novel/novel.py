#!/usr/bin/env python
# -*- coding=UTF-8 -*-
#*************************************************************************
#   File Name: novel.py
#   Author:JiangLin
#   Mail:xiyang0807@163.com
#   Created Time: 2015年10月19日 星期一 00时27分41秒
#*************************************************************************
import urllib
import urllib.request
from bs4 import BeautifulSoup
import re
import sys


class Tool:

    removeImg = re.compile('<img.*?>| {7}|')
    removeAddr = re.compile('<a.*?>|</a>')
    removeSpan = re.compile('<Span.*?>|</span>')
    replaceTD = re.compile('<td>')
    replaceSpace = re.compile('&nbsp;')
    replaceQuo = re.compile('&.*?quo')
    replaceBR = re.compile('<br><br>|<br>|<br><br><br>|<br><br><br><br>')
    removeExtraTag = re.compile('<.*?>')

    def replace(self, x):
        x = re.sub(self.removeImg, "", x)
        x = re.sub(self.removeAddr, "", x)
        x = re.sub(self.removeSpan, "", x)
        x = re.sub(self.replaceTD, "\t", x)
        x = re.sub(self.replaceSpace, "", x)
        x = re.sub(self.replaceQuo, "", x)
        x = re.sub(self.replaceBR, "\n", x)
        x = re.sub(self.removeExtraTag, "", x)
        return x.strip()


class Novel:
    def __init__(self):
        self.user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        self.headers = {'User-Agent': self.user_agent}
        self.tool = Tool()

    def getPage(self, url):
        try:
            url = 'http://tieba.baidu.com' + url + '?see_lz=1'
            request = urllib.request.Request(url, headers=self.headers)
            response = urllib.request.urlopen(request)
            pageCode = response.read().decode('utf-8')
            pattern = re.compile('<h3 class="core_title_txt.*?>(.*?)</h3>',
                                 re.S)
            items = re.findall(pattern, pageCode)
            for item in items:
                sys.stdout.write(self.tool.replace(item))
                sys.stdout.flush()
                print('\n')
            pattern = re.compile('<div id="post_content.*?>(.*?)</div>', re.S)
            items = re.findall(pattern, pageCode)
            for item in items:
                sys.stdout.write(self.tool.replace(item))
                sys.stdout.flush()
                print('')
                return
        except urllib.request.URLError as e:
            if hasattr(e, "reason"):
                print(u"连接baidu失败,错误原因", e.reason)
                return None

    def getPage1(self, url):
        url = 'http://tieba.baidu.com' + url + '?see_lz=1'
        request = urllib.request.Request(url, headers=self.headers)
        response = urllib.request.urlopen(url)
        content = response.read().decode("utf-8")
        soup = BeautifulSoup(content, "lxml")
        div_soup = soup.find_all("div", {'class': 'novel-post-content'})
        for td in div_soup:
            print(td.get_text('\n    ', '<br/><br/>'))

    def getChioce(self, url):
        url = url
        request = urllib.request.Request(url, headers=self.headers)
        response = urllib.request.urlopen(request)
        pattern = re.compile(
            '<ul id="thread_top_list.*?>(.*?)<i class="icon-top.*?>(.*?)<a href=\"(.*?)\".*?>(.*?)</ul>',
            re.S)
        content = response.read().decode('utf-8')
        items = re.findall(pattern, content)
        for item in items:
            self.getPage(item[2])

    def getChioce1(self, url):

        request = urllib.request.Request(url, headers=self.headers)
        response = urllib.request.urlopen(request)
        pattern = re.compile(
            '<ul id="thread_top_list.*?>(.*?)<i class="icon-top.*?>(.*?)<a href=\"(.*?)\".*?>(.*?)</ul>',
            re.S)
        content = response.read().decode('utf-8')
        items = re.findall(pattern, content)
        for item in items:
            self.getPage1(item[2])

    # 开始方法
    def start(self):
        print(u"请输入:")
        print(u"1.完美世界  2.我欲封天 3.天火大道 4.九阳踏天  5.戮仙")
        input1 = input()
        if input1 == '1':
            url = 'http://tieba.baidu.com/f?kw=%CD%EA%C3%C0%CA%C0%BD%E7%D0%A1%CB%B5&fr=ala0&loc=rec'
            self.getChioce(url)
        elif input1 == '2':
            url = 'http://tieba.baidu.com/f?kw=%CE%D2%D3%FB%B7%E2%CC%EC&fr=ala0&loc=rec'
            self.getChioce(url)
        elif input1 == '3':
            url = 'http://tieba.baidu.com/f?kw=%CC%EC%BB%F0%B4%F3%B5%C0&fr=ala0&loc=rec'
            self.getChioce(url)
        elif input1 == '4':
            url = 'http://tieba.baidu.com/f?kw=%BE%C5%D1%F4%CC%A4%CC%EC&fr=ala0&loc=rec'
            self.getChioce1(url)
        else:
            url = 'http://tieba.baidu.com/f?kw=%C2%BE%CF%C9&fr=ala0&loc=rec'
            self.getChioce1(url)


spider = Novel()
spider.start()
