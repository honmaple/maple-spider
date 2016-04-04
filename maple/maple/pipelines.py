# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from maple.models import News, DBSession,BsNews
#  from sqlalchemy.exc import IntegrityError,InvalidRequestError


class MaplePipeline(object):

    def process_item(self, item, spider):
        return item


class NewsPipeline(object):

    def open_spider(self, spider):
        self.session = DBSession()

    def process_item(self, item, spider):
        exsit_url = self.session.query(News.url).\
            filter_by(url=item['url']).first()
        if not exsit_url:
            news = News()
            news.title = item['title']
            news.url = item['url']
            news.time = item['time']
            news.content = item['content']
            #  self.session.begin(subtransactions=True)
            try:
                self.session.add(news)
                self.session.commit()
            except:
                self.session.rollback()

    def close_spider(self, spider):
        self.session.close()

class BsNewsPipeline(object):

    def open_spider(self, spider):
        self.session = DBSession()

    def process_item(self, item, spider):
        exsit_url = self.session.query(News.url).\
            filter_by(url=item['url']).first()
        if not exsit_url:
            news = BsNews()
            news.title = item['title']
            news.url = item['url']
            news.time = item['time']
            news.content = item['content']
            try:
                self.session.add(news)
                self.session.commit()
            except:
                self.session.rollback()

    def close_spider(self, spider):
        self.session.close()
