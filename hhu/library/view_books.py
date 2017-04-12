#*************************************************************************
#   Copyright © 2015 JiangLin. All rights reserved.
#   File Name: view_db.py
#   Author:JiangLin
#   Mail:xiyang0807@gmail.com
#   Created Time: 2015-10-26 07:29:25
#*************************************************************************
#!/usr/bin/env python
# -*- coding=UTF-8 -*-
import sqlite3

books = sqlite3.connect('books.db')
id = []
cursor = books.execute("SELECT * from BOOKS")
for row in cursor:
    print ("ID = %d "%(row[0]))
    print ("类型 = %s "%(row[1]))
    print ("BOOKNAME = %s "%(row[2]))
    print ("题名责任人 = %s "%(row[3]))
    print ("出版发行项 = %s "%(row[4]))
    print ("ISBN及定价 = %s "%(row[5]))
    print ("载体形态项 = %s "%(row[6]))
    print ("提要文摘附注 = %s "%(row[7]))
    print ("豆瓣简介 = %s "%(row[8]))
books.close()



