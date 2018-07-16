# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymysql

class ProjectPipeline(object):
    def process_item(self, item, spider):
        return item

class MysqlPipeline(object):
    def open_spider(self,spider):
        self.conn = pymysql.connect('127.0.0.1','root','123456','scrapy_project',charset='utf8')
        self.cursor = self.conn.cursor()


    def process_item(self,item,spider):
        try:
            sql,data = item.get_sql()
            self.cursor.execute(sql,data)
            self.conn.commit()

        except Exception as e:
            print(e)


        return item