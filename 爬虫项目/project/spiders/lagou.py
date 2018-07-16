# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from datetime import datetime 
import re 
from datetime import timedelta
import hashlib
from project.items import LagouItem

class LagouSpider(CrawlSpider):
    name = 'lagou'
    allowed_domains = ['lagou.com']
    start_urls = ['http://www.lagou.com/']


    custom_settings = {
        'DEFAULT_REQUEST_HEADERS' : {
            "Host": "www.lagou.com",
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 Safari/537.36",
            "Content-type": "application/json;charset=utf-8",
            "Accept": "*/*",
            "Referer": "https://www.lagou.com",
            "Accept-Language": "zh-CN,zh;q=0.9",
            "Cookie": "user_trace_token=20171116192426-b45997e2-cac0-11e7-98fd-5254005c3644; LGUID=20171116192426-b4599a6d-cac0-11e7-98fd-5254005c3644; index_location_city=%E5%85%A8%E5%9B%BD; JSESSIONID=ABAAABAAAGFABEFC0E3267F681504E5726030548F107348; _gat=1; X_HTTP_TOKEN=d8b7e352a862bb108b4fd1b63f7d11a7; _gid=GA1.2.1718159851.1510831466; _ga=GA1.2.106845767.1510831466; Hm_lvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1510836765,1510836769,1510837049,1510838482; Hm_lpvt_4233e74dff0ae5bd0a3d81c6ccf756e6=1510839167; LGSID=20171116204415-da8c7971-cacb-11e7-930c-525400f775ce; LGRID=20171116213247-a2658795-cad2-11e7-9360-525400f775ce",
        },
        'COOKIES_ENABLED' :False,
        'CONCURRENT_REQUESTS': 32,
        'MYSQL':{
            'host':'127.0.0.1',
            'user':'root',
            'password':'123456',
            'db':'scrapy_project'
        },
        'ITEM_PIPELINES':{
            'project.pipelines.MysqlPipeline':1
        }

    }

    rules = (
        Rule(LinkExtractor(allow=(r'list_',),tags=('a','form'),attrs=('href','action')),follow=True),
        Rule(LinkExtractor(allow=(r'lagou\.com/gongsi/',),tags=('a',),attrs=('href',)), follow=True),
        # 公司列表链接
        Rule(LinkExtractor(allow=(r'/gongsi/j\d+\.html',),tags=('a',),attrs=('href',)), follow=True),
        # 校园链接
        Rule(LinkExtractor(allow=(r'xiaoyuan\.lagou\.com',),tags=('a',),attrs=('href',)), follow=True),
        # 校园分类链接
        Rule(LinkExtractor(allow=(r'isSchoolJob',),tags=('a',),attrs=('href',)), follow=True),
        # 详情页
        Rule(LinkExtractor(allow=(r'jobs/\d+\.html',), tags=('a',), attrs=('href',)), callback='parse_item', follow=False),
        
 )

    num_pattern = re.compile(r'\d+')


    def parse_item(self, response):
        item = LagouItem()
        url = response.url
        pname = response.css('.job-name::attr(title)').extract_first()

        money = response.css('.job_request .salary::text').extract_first()
        smoney = money.lower().replace('k','').split('-')[0]
        emoney = money.lower().replace('k','').split('-')[1]

        location = response.css('.job_request span::text').extract()[1]
        location = self.remove_slash(location)
        # print(location)

        year = response.css('.job_request span::text').extract()[2]

        syear,eyear = self.process_year(year)
        # print(syear,eyear)
        # yield item
        degree = response.css('.job_request span::text').extract()[3]
        degree = self.remove_slash(degree)

        ptype = response.css('.job_request span::text').extract()[4]
        ptype = self.remove_slash(ptype)

        tags = response.css('.position-label li::text').extract()  # 获取职位所有标签
        tags = ','.join(tags) # 把所有标签连接成字符串
        # 发布日期
        date_pub = response.css('.publish_time::text').extract()[0].replace('发布于拉勾网','').strip()
        date_pub = self.process_date(date_pub)
        # print(date_pub)
        advantage = response.css('.job-advantage p::text').extract()[0]

        jobdesc = response.css('.job_bt div p::text').extract()
        jobdesc = ''.join(jobdesc)
        # print(jobdesc)
        jobaddr1 = response.css('.work_addr a::text').extract()[:-1]
        jobaddr2 = response.css('.work_addr::text').extract()[2].strip()
        # print(jobaddr1)
        jobaddr='-'.join(jobaddr1)+jobaddr2
        # print(jobaddr)

        company = response.css('#job_company dt a img::attr(alt)').extract()[0]
        # 抓取时间
        crawl_time = datetime.now().strftime('%Y-%m-%d')

        item['url'] = url
        item['url_id'] = self.md5(url)
        item['pname'] = pname
        item['smoney'] = smoney
        item['emoney'] = emoney
        item['location'] = location
        item['syear'] = syear
        item['eyear'] = eyear
        item['degree'] = degree
        item['ptype'] = ptype
        item['tags'] = tags
        item['date_pub'] = date_pub
        item['advantage'] = advantage
        item['jobdesc'] = jobdesc
        item['jobaddr'] = jobaddr
        item['company'] = company
        item['crawl_time'] = crawl_time
        item['spider_name'] = 'lagou'

        yield item
    
    def remove_slash(self,value):
        value = value.replace('/','').strip()
        return value


    # def process_year(self,value):
    #     if '-' in value:
    #         res = self.num_pattern.findall(value)
    #         syear = res[0]
    #         eyear = res[1]
    #         print(syear,'dao',eyear)
    #     elif '年以上' in value:
    #         res = self.num_pattern.findall(value)
    #         syear = res[0]
    #         eyear = res[0]
    #         print(syear,'yishang')
    #     else:
    #         syear = 0
    #         eyear = 0

    #     return syear,eyear
    def process_year(self,year):
        if '-' in year:  # 3-5年
            res = self.num_pattern.findall(year) # 返回列表
            syear = res[0]
            eyear = res[1]
        elif '以上' in year:   # 3年以上
            res = self.num_pattern.search(year)
            syear = res.group()
            eyear = res.group()
        else: # 其它
            syear = 0
            eyear = 0
        return syear,eyear

    def process_date(self,value):
        if '-' in value:
            date_pub = value
        elif ':' in value:
            date_pub = datetime.now().strftime('%Y-%m-%d')
            # print(datetime.now())
        elif '天前' in value:
            res = self.num_pattern.search(value).group()
            date_pub = (datetime.now() - timedelta(days=int(res))).strftime('%Y-%m-%d')

        return date_pub

    def md5(self,value):
        m = hashlib.md5()
        m.update(bytes(value,encoding='utf-8'))
        return m.hexdigest()