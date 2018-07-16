import scrapy
from project.items import Job51Item
import time
import re
from datetime import datetime,timedelta
import hashlib
class Job51(scrapy.Spider):
    name = 'job'
    allowed_domains = []
    start_urls = ['http://www.51job.com']
    base_url = 'https://search.51job.com/list/010000,000000,0000,00,9,99,%2520,2,{}.html?lang=c&stype=&postchannel=0000&workyear=99&cotype=99&degreefrom=99&jobterm=99&companysize=99&providesalary=99&lonlat=0%2C0&radius=-1&ord_field=0&confirmdate=9&fromType=&dibiaoid=0&address=&line=&specialarea=00&from=&welfare='
    num_pattern = re.compile(r'\d+')
    custom_settings = {
    'DEFAULT_REQUEST_HEADERS' : {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
            "Cookie" :"adv=adsnew%3D1%26%7C%26adsresume%3D1%26%7C%26adsfrom%3Dhttps%253A%252F%252Fwww.baidu.com%252Fs%253Fwd%253D%2525E5%252589%25258D%2525E7%2525A8%25258B%2525E6%252597%2525A0%2525E5%2525BF%2525A7%2526rsv_spt%253D1%2526rsv_iqid%253D0x861c6f3200000f4d%2526issp%253D1%2526f%253D8%2526rsv_bp%253D1%2526rsv_idx%253D2%2526ie%253Dutf-8%2526rqlang%253Dcn%2526tn%253Dbaiduhome_pg%2526rsv_enter%253D1%2526oq%253D%252525E7%25252588%252525AC%252525E8%25252599%252525AB%252525E8%2525258E%252525B7%252525E5%2525258F%25252596%252525E6%252525A0%25252587%252525E7%252525AD%252525BE%252525E7%2525259A%25252584%252525E5%252525B1%2525259E%252525E6%25252580%252525A7%252525E5%25252580%252525BC%2526rsv_t%253D257fIhZqi5OCnqGGcz5lZRqeexx93MD1KDtRU4iMguWd%25252FZcieOK05izIYxVMXfx3LCV8%2526inputT%253D10423%2526rsv_pq%253D8e7d6869000025a7%2526rsv_sug3%253D128%2526rsv_sug1%253D94%2526rsv_sug7%253D100%2526bs%253D%2525E7%252588%2525AC%2525E8%252599%2525AB%2525E8%25258E%2525B7%2525E5%25258F%252596%2525E6%2525A0%252587%2525E7%2525AD%2525BE%2525E7%25259A%252584%2525E5%2525B1%25259E%2525E6%252580%2525A7%2525E5%252580%2525BC%26%7C%26adsnum%3D2004282; partner=baidupz; 51job=cenglish%3D0%26%7C%26; guid=15306214112959950070; nsearch=jobarea%3D%26%7C%26ord_field%3D%26%7C%26recentSearch0%3D%26%7C%26recentSearch1%3D%26%7C%26recentSearch2%3D%26%7C%26recentSearch3%3D%26%7C%26recentSearch4%3D%26%7C%26collapse_expansion%3D; search=jobarea%7E%60010000%7C%21ord_field%7E%600%7C%21recentSearch0%7E%601%A1%FB%A1%FA010000%2C00%A1%FB%A1%FA000000%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA2%A1%FB%A1%FA%A1%FB%A1%FA-1%A1%FB%A1%FA1530621418%A1%FB%A1%FA0%A1%FB%A1%FA%A1%FB%A1%FA%7C%21recentSearch1%7E%601%A1%FB%A1%FA010000%2C00%A1%FB%A1%FA000000%A1%FB%A1%FA0000%A1%FB%A1%FA00%A1%FB%A1%FA9%A1%FB%A1%FA99%A1%FB%A1%FA09%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA99%A1%FB%A1%FA%A1%FB%A1%FA2%A1%FB%A1%FA%A1%FB%A1%FA-1%A1%FB%A1%FA1530622106%A1%FB%A1%FA0%A1%FB%A1%FA%A1%FB%A1%FA%7C%21"
        },
        'RETRY_TIMES' : 5, # 下载器重试次数
        'DOWNLOAD_TIMEOUT' : 3, # 3秒以后请求超时
        'CONCURRENT_REQUEST' : 64,
        'ITEM_PIPELINES' : {
            'project.pipelines.MysqlPipeline' : 1,
        }
    }

    def parse(self,response):
        # print(response.url)
        for i in range(1,2001):
            fullurl = self.base_url.format(i)

            req = scrapy.Request(fullurl,callback=self.parse_list)
            # print(fullurl)
            yield req

    def parse_list(self,response):
        res=response.xpath('//*[@class="dw_table"]//div[@class="el"]/p/span/a/@href').extract()
        for i in res:
            detail_url=i
            yield scrapy.Request(detail_url,callback=self.parse_detail)


    def parse_detail(self,response):
        item = Job51Item()


        url = response.url
        pname = response.xpath('//div[3]/div[2]/div[2]/div/div[1]/h1/text()').extract()[0]
        money = response.xpath('//div[3]/div[2]/div[2]/div/div[1]/strong/text()').extract_first()
        smoney,emoney,ptype = self.parse_money(money)
        location = response.xpath('//div[3]/div[2]/div[2]/div/div[1]/span/text()').extract_first()
        info = response.xpath('//div[3]/div[2]/div[3]/div[1]/div/div').css('span::text').extract()
        syear,eyear = self.parse_year(info[0])
        degree = info[1]
        date_pub = response.xpath('//div[3]/div[2]/div[3]/div[1]/div/div/span[4]/text()').extract()[0]
        tags = response.xpath('//div[3]/div[2]/div[2]/div/div[1]/p[2]/text()').extract()[0].replace(' ','').strip().replace('\t','')
        advantage = response.xpath('//div[3]/div[2]/div[3]/div[1]/div/p').css('span::text').extract()
        # print(smoney,'-----',emoney)
        if len(advantage)>0:
            advantage = '-'.join(advantage)
        else:
            advantage = '没有福利'
        # print(advantage)
        jobdesc = response.xpath('//div[3]/div[2]/div[3]/div[2]').css('.job_msg p::text').extract()
        jobdesc = ','.join(jobdesc).strip().replace(' ','').replace(',','').strip()
        jobaddr = response.xpath('//div[3]/div[2]/div[3]/div[3]/div/p/text()').extract()[1].strip()
        # jobdesc = response.xpath('//div[3]/div[2]/div[3]/div[2]/div//p[1]/text()').extract()
        company = response.xpath('//div[3]/div[2]/div[2]/div/div[1]/p[1]/a/@title').extract()[0]
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
        item['spider_name'] = 'job51'

        yield item
        # print(tags)
        
    def parse_money(self,value):
        if '万/月' in value:
            # print(value+'--------')
            money = value.replace('万/月','').split('-')
            smoney = float(money[0])*10000
            emoney = float(money[1])*10000
            ptype = '全职'

        elif '千/月' in value:
            # print(value)
            money = value.replace('千/月','').split('-')
            smoney = float(money[0])*1000
            emoney = float(money[1])*1000
            ptype = '全职'

        elif '年' in value:
            # print(value)

            money = value.replace('万/年','').split('-')
            smoney = int(int(money[0])/12*10000)
            emoney = int(int(money[1])/12*10000)
            ptype = '全职'

        elif '天' in value:
            smoney = value
            emoney = value
            ptype = '兼职'
        else:
            smoney = '面议'
            emoney = '面议'
            ptype = '全职'


        return smoney,emoney,ptype

    def parse_year(self,value):
        if '无' in value:
            syear = 0
            eyear = 0
        elif '-' in value:
            syear = value.replace('年经验','').split('-')[0]
            eyear = value.replace('年经验','').split('-')[1]
        elif '年经验' in value and '-' not in value:
            syear = value.replace('年经验','')
            eyear = value.replace('年经验','')+'+'
        
        else:
            pass
        return syear,eyear

    def md5(self,value):
        m = hashlib.md5()
        m.update(bytes(value,encoding='utf-8'))
        return m.hexdigest()