# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html

import csv
from IMBD_Spider.SQL_Manager import sql_manager, IMBD_movie_url_SQL

class ImbdSpiderPipeline(object):

    def __init__(self):
        # self.file = open('D:/hongkong record/daily course/second seminster/COMP7630/Projectmovie_urls.csv', 'wb')
        # self.writter = csv.writer(self.file)
        print('pipline start')

    def close_spider(self, spider):
        # self.file.close()
        pass

    def process_item(self, item, spider):
        # self.writter.writerow([item['title'], item['url']])
        pass



