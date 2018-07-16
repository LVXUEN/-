# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


# class ProjectItem(scrapy.Item):
#     # define the fields for your item here like:
#     # name = scrapy.Field()
#     pass
class ProjectItem(scrapy.Item):
    url = scrapy.Field()
    url_id = scrapy.Field()
    pname = scrapy.Field()
    smoney = scrapy.Field()
    emoney = scrapy.Field()
    location = scrapy.Field()
    syear = scrapy.Field()
    eyear = scrapy.Field()
    degree = scrapy.Field() # 学历
    ptype = scrapy.Field() # 职位类型
    tags = scrapy.Field() # 标签
    date_pub = scrapy.Field() # 发布日期
    advantage = scrapy.Field() # 职位诱惑
    jobdesc = scrapy.Field() # 职位简介
    jobaddr = scrapy.Field() # 职位要求
    company = scrapy.Field() # 公司
    spider_name = scrapy.Field()
    crawl_time = scrapy.Field() # 抓取时间

    def get_sql(self):
        sql = 'insert into lagou_job(url,url_id,pname,smoney,emoney,location,syear,eyear,degree,ptype,tags,date_pub,advantage,jobdesc,jobaddr,company,spider_name,crawl_time) values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
        data = (self['url'],self['url_id'],self['pname'],self['smoney'],self['emoney'],self['location'],self['syear'],self['eyear'],self['degree'],self['ptype'],self['tags'],self['date_pub'],self['advantage'],self['jobdesc'],self['jobaddr'],self['company'],self['spider_name'],self['crawl_time'])
        return sql,data
        

class LagouItem(ProjectItem):
    pass



class ZhiLianItem(ProjectItem):
    pass


class LiePinItem(ProjectItem):
    pass

class Job51Item(ProjectItem):
    pass