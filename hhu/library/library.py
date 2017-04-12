#!/usr/bin/env python
# -*- coding=UTF-8 -*-
#*************************************************************************
#   File Name: libriry.py
#   Author:JiangLin
#   Mail:xiyang0807@gmail.com
#   Created Time: 2015年10月21日 星期三 06时17分56秒
#*************************************************************************
import sys
from bs4 import BeautifulSoup
import urllib
import urllib.request
from selenium import webdriver


class libriry:

    def __init__(self):
        self.user_agent = [{'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},
                           {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'},
                           {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'}]
        self.headers = {'User-Agent': self.user_agent}
        self.url1 = 'http://210.29.99.7:8080/opac/openlink.php?dept=ALL&title='
        self.url2 = '&doctype=ALL&lang_code=ALL&match_flag=forward&displaypg=20'
        self.url3 = '&showmode=list&orderby=DESC&sort=CATA_DATE&onlylendable=no&count=482&with_ebook=&page='

    def getPage(self, url, search, page, num, href_num):
        try:
            url = url
            # 构建请求的request
            request = urllib.request.Request(url)
            # 利用urlopen获取页面代码
            response = urllib.request.urlopen(request)
            content = response.read().decode('utf-8')
            book = str(content)
            book_soup = BeautifulSoup(book, "lxml")
            # book_view = book_soup.find_all('div',{'class':'book_article'})
            # MARC状态
            book_view = book_soup.find_all('p', {'id': 'marc'})
            for view in book_view:
                print(
                    view.get_text().replace(
                        '\n',
                        '').replace(
                        '            ',
                        ''))
            book_indro = book_soup.find_all('dl', {'class': 'booklist'})
            print('========================================')
            for item in book_indro:
                print(item.get_text('', strip=True))
            # 使用PhantomJS解析json
            driver = webdriver.PhantomJS()
            driver.get(url)
            data = driver.find_element_by_id('intro').text
            print(data)
            driver.quit()
            # print(book_item_indro.select('p',{'id':'intro'}))
            # 馆藏信息
            book_tab_item = book_soup.find('a', {'href': '#tab_item'})
            print("\n", book_tab_item.string)
            # 查看是否可借阅
            book_tab_item_table = book_soup.find('table')
            book_tab_tr = book_tab_item_table.find_all('tr')
            for tr in book_tab_tr:
                print(tr.get_text().replace('\n', '  '))
            print(u"\n序号 %s  (q:返回 Q:退出 ENTER:下一本书籍)" % (num))
            input1 = input()
            if input1 == 'q':
                self.getUrl(search, page)
            elif input1 == 'Q':
                sys.exit()
            else:
                # 单页结果输出完毕
                if (int(num)-(int(page)-1)*20) == 20:
                    page += 1
                num = int(num) + 1
                self.getBook(search, page, num, href_num)
        except (urllib.request.HTTPError, urllib.request.URLError) as e:
            print(e)
            sys.exit()

    def getBook(self, search, page, num, href_num):  # 显示下一本书籍的内容
        # 介绍页循环
        if (int(num)-20*(int(page)-1)) <= href_num:
            url = self.url1 + str(search) + self.url2 + self.url3 + str(page)
            request = urllib.request.Request(url)
            # 利用urlopen获取页面代码
            response = urllib.request.urlopen(request)
            content = response.read().decode('utf-8')
            book_content = str(content)
            self.soup = BeautifulSoup(book_content, "lxml")
            h3_soup = self.soup.find_all('h3')
            href = h3_soup[int(num)-1-20*(int(page)-1)].a.get('href')
            # 异常处理，循环到搜索结果最后一项
            try:
                url3 = 'http://210.29.99.7:8080/opac/' + href
                self.getPage(url3, search, page, num, href_num)
            except:
                print(u"已经没有相符的书籍了")
               # spider.start()
        else:
            print(u"已经没有相符的书籍了")
            spider.start()

    def getUrl(self, search, page):
        # 该循环为搜索结果循环
        while True:
            search = search
            page = page
            url = self.url1 + str(search) + self.url2 + self.url3 + str(page)
        #  self.getUrl(url1,url2,url3,search,page)
            request = urllib.request.Request(url)
            # 利用urlopen获取页面代码
            response = urllib.request.urlopen(request)
            content = response.read().decode('utf-8')
            book_content = str(content)
            self.soup = BeautifulSoup(book_content, "lxml")
            h3_soup = self.soup.find_all('h3')
            href_num = 0
            if h3_soup:
                # 异常判断，如果page得到结果为空则重新搜索
                for h3 in h3_soup:
                    # 用replace去除不相关的内容
                    href_num += 1
                    print(
                        h3.get_text().replace(
                            '中文图书',
                            '').replace(
                            '西文图书',
                            '').replace(
                            '规范文档',
                            ''))
                print(u"第 %s 页     (q:返回 Q:退出 ENTER:下一页)" % (page))
                num = input(u"请选择书籍: ")
                if num != '':
                    if num == 'Q':
                        sys.exit()
                    elif num == 'q':
                        spider.start()
                    else:
                        # 这里必须按照序号输入，否则会出错
                        href = h3_soup[
                            int(num)-1-20*(int(page)-1)].a.get('href')
                        url = 'http://210.29.99.7:8080/opac/' + href
                        self.getPage(url, search, page, num, href_num)
                else:
                    page += 1
            else:
                print(u"已经没有相符的书籍了")
                spider.start()

    def start(self):
        print(u"请输入要搜索的书籍名称")
        search = input()
        if search == 'q':
            sys.exit()
        page = 1
        self.getUrl(search, page)

# 程序入口
spider = libriry()
spider.start()

