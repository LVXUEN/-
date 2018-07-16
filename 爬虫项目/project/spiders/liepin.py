import scrapy
import json
from project.items import LiePinItem
import time
import re
from datetime import datetime,timedelta
import hashlib

class LiePin(scrapy.Spider):
    name = 'liepin'
    allowed_domains = []
    start_urls = ['http://www.liepin.com']
    base_urls = 'https://www.liepin.com/zhaopin/?ckid=8738bbdbef4e9282&fromSearchBtn=2&degradeFlag=0&init=-1&sfrom=click-pc_homepage-centre_searchbox-search_new&key=&headckid=8738bbdbef4e9282&d_pageSize=40&siTag=1B2M2Y8AsgTpgAmY7PhCfg~fA9rXquZc5IkJpXC-Ycixw&d_headId=89a77944f1930e2f793f204346f5d66b&d_ckId=89a77944f1930e2f793f204346f5d66b&d_sfrom=search_fp&d_curPage=0&curPage=%d'
    num_pattern = re.compile(r'\d+')
    custom_settings = {
    'DEFAULT_REQUEST_HEADERS' : {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
            "Cookie":"appguide=yes; abtest=0; _fecdn_=1; __uuid=1530603606622.77; _mscid=s_00_pz0; _uuid=5F15EBBEFFA844194AC27B0AA613A9BF; Hm_lvt_a2647413544f5a04f00da7eee0d5e200=1530603608; slide_guide_home_new=1; slide_guide_home=1; ADHOC_MEMBERSHIP_CLIENT_ID1.0=b38416c1-b059-4663-0ca1-5c577e69fd0c; firsIn=1; __tlog=1530603606623.69%7C00000000%7CR000000075%7Cs_00_pz0%7Cs_00_pz0; verifycode=13c08731ae534b95a5ce664115947d47; JSESSIONID=C4F154FDE13CE45468ED370F9E5DD908; __session_seq=26; __uv_seq=26; Hm_lpvt_a2647413544f5a04f00da7eee0d5e200=1530604582"
        },
        'RETRY_TIMES' : 5, # 下载器重试次数
        'DOWNLOAD_TIMEOUT' : 3, # 3秒以后请求超时
        'CONCURRENT_REQUEST' : 64,
        'ITEM_PIPELINES' : {
            'project.pipelines.MysqlPipeline' : 1,
        }
    }

    def parse(self,response):
        for i in range(0,101):
            fullurl = self.base_urls % i 
            req = scrapy.Request(fullurl,callback = self.parse_list)
            yield req


    def parse_list(self,response):
        # res = response.text
        # print(res)
        detail_url = response.xpath('//*[@class="sojob-list"]/li//h3/a/@href').extract()
        for i in detail_url :
            
            yield scrapy.Request(i,callback = self.parse_detail)

    def parse_detail(self,response):

        # print(response.text)
        # time.sleep(200)

        item = LiePinItem()

        url = response.url
        pname = response.xpath('//*[@id="job-view-enterprise"]//div[@class="title-info"]/h1/text()').extract_first()
        money = response.xpath('//*[@id="job-view-enterprise"]//div[@class="job-title-left"]/p/text()').extract()[0]
        smoney,emoney = self.parse_money(money)
        location = response.css('.basic-infor span a::text').extract_first()
        year = response.css('.job-qualifications span::text').extract()[1]
        syear,eyear = self.parse_year(year)
        degree = response.css('.job-qualifications span::text').extract()[0]
        ptype = '全职'
        tags = '-猎聘网-'.join(response.css('.job-qualifications span::text').extract()[2:])
        
        date_pub = response.css('.basic-infor').xpath('./time/@title').extract_first()
        advantage ='-'.join(response.css('.tag-list span::text').extract())
        # jobdesc = ','.join(response.css('.content-word::text').extract()).replace(' ','').strip()
        jobdesc =','.join(response.css('.content-word::text').extract()[:-6])
        jobaddr = response.xpath('//*[@class="new-compwrap"]/ul[1]/li[3]/text()').extract()[0]
        company = response.xpath('//*[@class="title-info"]/h3[1]/a/text()').extract_first()
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
        item['spider_name'] = 'zhilian'

        yield item

        # print(company)




    def parse_money(self,value):
        if '面议' in value:
            smoney = '面议'
            emoney = '面议'
        else:

            money=value.replace('万','').strip().split('-')
            smoney = int(int(money[0])*10000/12)
            emoney = int(int(money[1])*10000/12)
        return smoney,emoney
        # return 1,2 

    def parse_year(self,value):
        if '不限' in value:
            syear = 0
            eyear = 0
        else:
            year = self.num_pattern.search(value).group()
            syear = year
            eyear = str(year)+'+'
        return syear,eyear

    def md5(self,value):
        m = hashlib.md5()
        m.update(bytes(value,encoding='utf-8'))
        return m.hexdigest()