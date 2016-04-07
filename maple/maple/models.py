#!/usr/bin/env python
# -*- coding=UTF-8 -*-
#*************************************************************************
# Copyright © 2015 JiangLin. All rights reserved.
# File Name: models.py
# Author:JiangLin
# Mail:xiyang0807@gmail.com
# Created Time: 2016-04-04 13:50:54
# Last Update: 2016-04-04 19:58:59
#          By: jianglin
# Description:
#*************************************************************************
from sqlalchemy import Column, String, Integer, Text,DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine


engine = create_engine('sqlite:///news.db', echo=True)
DBSession = sessionmaker(bind=engine)

Base = declarative_base()


class News(Base):
    __tablename__ = 'news'
    id = Column(Integer, primary_key=True)
    title = Column(String(60),nullable=False)
    url = Column(String(100),unique=True,nullable=False)
    time = Column(DateTime,nullable=False)
    content = Column(Text,nullable=False)
    category = Column(String(20),nullable=False)

Base.metadata.create_all(engine)
