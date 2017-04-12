#!/usr/bin/env python
# -*- coding=UTF-8 -*-
#*************************************************************************
#   File Name: hhuc.py
#   Author:JiangLin
#   Mail:xiyang0807@163.com
#   Created Time: 2015年10月18日 星期日 08时19分27秒
#*************************************************************************

import re
import urllib
import urllib2


class Tool:
    removeImg = re.compile('<img.*?>| {7}|')
    removeAddr = re.compile('<a.*?>|</a>')
    removeSpan = re.compile('<Span.*?>|</span>')
    replaceLine = re.compile('<tr>|<div>|</div>|</p>')
    replaceTD = re.compile('<td>')
    replaceSpace = re.compile('&nbsp;')
    replaceQuo = re.compile('&.*?quo')
    replacePara = re.compile('<font.*?>')
    replaceBR = re.compile('<br><br>|<br>')
    removeExtraTag = re.compile('<.*?>')

    def replace(self, x):
        x = re.sub(self.removeImg, "", x)
        x = re.sub(self.removeAddr, "", x)
        x = re.sub(self.removeSpan, "", x)
        x = re.sub(self.replaceLine, "\n", x)
        x = re.sub(self.replaceTD, "\t", x)
        x = re.sub(self.replaceSpace, "", x)
        x = re.sub(self.replaceQuo, "", x)
        x = re.sub(self.replacePara, "\n  ", x)
        x = re.sub(self.replaceBR, "\n", x)
        x = re.sub(self.removeExtraTag, "", x)
        return x.strip()


class hhuc:
    def __init__(self):
        self.pageIndex = 1
        self.user_agent = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        self.headers = {'User-Agent': self.user_agent}
        self.tool = Tool()
        self.enable = False

    def getPage(self, pageIndex, url):
        try:
            url = url + str(pageIndex) + '/list.htm'
            request = urllib2.Request(url, headers=self.headers)
            response = urllib2.urlopen(request)
            pageCode = response.read().decode('utf-8')
            return pageCode

        except urllib2.URLError, e:
            if hasattr(e, "reason"):
                print u"连接hhuc失败,错误原因", e.reason
                return None

    def getPageItems(self, pageIndex, url, urlItem):
        pageCode = self.getPage(pageIndex, url)
        if not pageCode:
            print "页面加载失败...."
            return None
        pattern = re.compile(
            '<td><a href=\'(.*?)\'.*?target.*?>.*?<font color.*?>(.*?)</font></a></td>',
            re.S)
        items = re.findall(pattern, pageCode)
        for item in items:
            print "========================================================"
            print item[1]
            print "========================================================"
            self.getItem(item[0], urlItem)
            input1 = raw_input()
            if input1 == 'Q':
                self.enable = False
                return
            elif input1 == 'q':
                spider.start()

        input = raw_input()
        if input == 'Q':
            self.enable = False
            return
        elif input1 == 'q':
            spider.start()
        pageIndex += 1
        self.getPageItems(pageIndex)

    def getItem(self, page, urlItem):
        url = urlItem + str(page)
        request = urllib2.Request(url, headers=self.headers)
        response = urllib2.urlopen(request)
        pattern = re.compile('<p.*?>.*?</p>', re.S)
        pageCode = response.read().decode('utf-8')
        items = re.findall(pattern, pageCode)
        for item in items:
            print self.tool.replace(item)
        return

    #开始方法
    def start(self):
        print u"q:返回     Q:退出"
        print u"请输入需要爬取的内容:"
        print "=================================="
        print u"1.学校新闻       2.学院公告"
        print "=================================="
        pageIndex = 1
        self.enable = True
        self.chioce = raw_input()
        if self.chioce == '1':
            url = 'http://202.119.112.75/s/2001/t/2016/p/5/i/'
            urlItem = 'http://202.119.112.75'
            self.getPageItems(pageIndex, url, urlItem)
        elif self.chioce == '2':
            url = 'http://wulwxy.hhuc.edu.cn/s/2059/t/2561/p/5/i/'
            urlItem = 'http://wulwxy.hhuc.edu.cn'
            self.getPageItems(pageIndex, url, urlItem)
        else:
            print u"输入错误请从新输入:"
            spider.start()
        #先加载一页内容


spider = hhuc()
spider.start()
