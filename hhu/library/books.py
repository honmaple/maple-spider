#*************************************************************************
#   Copyright © 2015 JiangLin. All rights reserved.
#   File Name: sqlite.py
#   Author:JiangLin
#   Mail:xiyang0807@gmail.com
#   Created Time: 2015-10-26 07:36:41
#   豆瓣分类
#*************************************************************************
#!/usr/bin/env python
# -*- coding=UTF-8 -*-
import urllib
import urllib.request
from bs4 import BeautifulSoup
import re
import sqlite3
# import pdb
from selenium import webdriver


try:

    url = 'http://210.29.99.7:8080/top/top_lend.php'
    user_agent = [{'User-Agent': 'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.1.6) Gecko/20091201 Firefox/3.5.6'},
                  {'User-Agent': 'Mozilla/5.0 (Windows NT 6.2) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.12 Safari/535.11'},
                  {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.2; Trident/6.0)'}]
    headers = {'User-Agent': user_agent}
    request = urllib.request.Request(url, headers=headers)
    response = urllib.request.urlopen(url)
    content = response.read().decode('utf-8')
    book_content = str(content)
    # 打开数据库
    books = sqlite3.connect('books.db', check_same_thread=False)
    print("Opened database successfully")
    # 创建数据库，如果数据库以存在则插入数据
    try:
        books.execute('''CREATE TABLE BOOKS
            (ID   INT   NOT NULL,
            TYPE TEXT NOT NULL,
            NAME TEXT NOT NULL,
            DUTY  TEXT,
            PUBLISH TEXT,
            ISBN TEXT,
            FORMS TEXT,
            GEN TEXT,
            DOU TEXT);''')
    except:
        # pdb.set_trace()
        soup = BeautifulSoup(book_content, "lxml")
        main_soup = soup.find('div', {'id': 'mainbox'})
        # 正则匹配cls_no的链接
        main_href = soup.find_all(href=re.compile("cls_no"))
        print(main_href)
        # num ID数目
        num = 0
        # 删除数据库,本来是更新数据库的，小数据直接删除了
        books.execute("DELETE from BOOKS")
        for href in main_href:
            print(href.get_text())
            url = 'http://210.29.99.7:8080/top/top_lend.php' + href.get('href')
            request = urllib.request.Request(url, headers=headers)
            response = urllib.request.urlopen(url)
            content = response.read().decode('utf-8')
            book_list_content = str(content)
            book_list_soup = BeautifulSoup(book_list_content, "lxml")
            book_list_list = book_list_soup.find_all('a', {'class': 'blue'})
            for book1 in book_list_list:
                num += 1
                print(book1.get_text())
                book_list_href = book1.get('href').replace('..', '')
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
                    print('========================================')
                    # 这里太耽搁时间，将CONTENT内容传入数据库
                    # books.execute("INSERT INTO BOOKS (ID,类型,书名) \
                    # VALUES
                    # ('%d','%s','《%s》')"%(num,href.get_text(),book1.get_text()));
                    ber = 0
                    book_dt = book_item_soup.find_all('dt')
                    book_dd = book_item_soup.find_all('dd')
                    for book in book_item_indro:
                        ber += 1
                        # b = re.compile(u"[\u4e00-\u9fa5]+:[\n]?")
                        # c = b.findall(book.get_text())
                        # print(c)
                    # pdb.set_trace()
                    # 使用PhantomJS解析json
                    driver = webdriver.PhantomJS()
                    driver.get(url)
                    data = driver.find_element_by_id('intro').text
                    print(data)
                    driver.quit()
                    print(book1.get_text())
                    print(book_dt[ber-3].get_text())
                    print(book_dd[ber-3].get_text())
                    books.execute(
                        "INSERT INTO BOOKS (ID,TYPE,NAME,DUTY,PUBLISH,ISBN,FORMS,GEN,DOU) \
                            VALUES ('%d','%s','《%s》','%s','%s','%s','%s','%s','%s')" % (num,
                                                                                        href.get_text(),
                                                                                        book1.get_text(),
                                                                                        book_dd[0].get_text(),
                                                                                        book_dd[1].get_text(),
                                                                                        book_dd[2].get_text(),
                                                                                        book_dd[3].get_text(),
                                                                                        book_dd[
                                                                                            -3].get_text(),
                                                                                        data))

#             t = threading.Thread(target=hello,args=(href,num))
            # threads.append(t)
#             num += 100

except:
    books.commit()
    books.close()

