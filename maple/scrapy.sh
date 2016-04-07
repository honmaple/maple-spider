#!/bin/bash
echo "正在爬取学校新闻"
scrapy crawl news
echo "正在爬取企业管理学院新闻"
scrapy crawl bs
echo "正在爬取机电学院新闻"
scrapy crawl jidian
echo "正在爬取物联网学院新闻"
scrapy crawl wulwxy
i=1
while(($i<=3))
do
espeak "the task has completed"
sleep 1
i=$i+1
done
