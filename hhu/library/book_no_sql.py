#!/usr/bin/env python
# -*- coding=UTF-8 -*-
#*************************************************************************
#   File Name: bs.py
#   Author:JiangLin
#   Mail:xiyang0807@gmail.com
#   Created Time: 2015年10月19日 星期一 20时48分35秒
#*************************************************************************
import sys
import re
from bs4 import BeautifulSoup
import urllib
import urllib.request


try:
    # 目标网址
    url = 'http://210.29.99.7:8080/top/top_lend.php'
    # 伪装成浏览器
    user_agent = [{'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},
                  {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'},
                  {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'}]
    headers = {'User-Agent': user_agent}
    request = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(url)
    content = response.read().decode('utf-8')
    book_content = str(content)
    # 将网页内容传递给book
    # book(book_content)

    soup = BeautifulSoup(book_content, "lxml")
    main_soup = soup.find('div', {'id': 'mainbox'})
    # 正则匹配cls_no的链接
    main_href = soup.find_all(href=re.compile("cls_no"))
    # 目录链接
    for href in main_href:
        print(href.get_text())
        input1 = input()
        if input1 == 'q':
            sys.exit()
        url = 'http://210.29.99.7:8080/top/top_lend.php' + href.get('href')
        request = urllib.request.Request(url, headers=headers)
        response = urllib.request.urlopen(url)
        content = response.read().decode('utf-8')
        book_list_content = str(content)
        book_list_soup = BeautifulSoup(book_list_content, "lxml")
        book_list_list = book_list_soup.find_all('a', {'class': 'blue'})
        for book1 in book_list_list:
            print(book1.get_text())
        input2 = input()
        # 查找书籍链接
        book_list_view = book_list_soup.find_all(href=re.compile("opac"))
        for book in book_list_view:
            # 去掉..
            book_list_href = book.get('href').replace('..', '')
            # 去除不必要的链接
            if book_list_href == '/opac/book_cart.php':
                continue
            elif book_list_href == '/opac/search.php':
                continue
            elif book_list_href == '/opac/book_cart.php':
                continue
            else:
                url = 'http://210.29.99.7:8080' + book_list_href
                request = urllib.request.Request(url, headers=headers)
                response = urllib.request.urlopen(url)
                content = response.read().decode('utf-8')
                book_item_content = str(content)
                book_item_soup = BeautifulSoup(book_item_content, "lxml")
                book_item_indro = book_item_soup.find_all(
                    'dl', {'class': 'booklist'})
                # book_item_indro = book_item_soup.find_all('div',{'id':'item_detail'})
                print('========================================')
                for item in book_item_indro:
                    print(item.get_text('', strip=True))
                # print(book_item_indro.select('p',{'id':'intro'}))
                input3 = input()
                if input3 == 'q':
                    sys.exit()

except (urllib.request.HTTPError, urllib.request.URLError) as e:
    print(e)
    sys.exit()
