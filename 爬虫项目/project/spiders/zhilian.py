import scrapy
import json
from project.items import ZhiLianItem
import time
import re
from datetime import datetime,timedelta
import hashlib
class ZhiLian(scrapy.Spider):
    name = 'zhilian'
    allowed_domains = []  # 爬虫允许爬取得有效域，限制除了start_urls以外的请求
    start_urls = ['http://www.zhaopin.com']
    # base_url = 'https://fe-api.zhaopin.com/c/i/sou?start=%d&pageSize=60&cityId=530&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=-1&kt=3'
    base_url = 'https://fe-api.zhaopin.com/c/i/sou?start=%d&pageSize=60&cityId=530&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=-1&sortType=publish&kt=3'
    # base_url = 'https://fe-api.zhaopin.com/c/i/sou?pageSize=60&cityId=530&workExperience=-1&education=-1&companyType=-1&employmentType=-1&jobWelfareTag=-1&kt=3'
    num_pattern = re.compile(r'\d+')
    custom_settings = {
    'DEFAULT_REQUEST_HEADERS' : {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
            "Cookie":"adfbid2=0; dywem=95841923.y; _jzqa=1.4314559635567621600.1528787729.1528787729.1528787729.1; _jzqx=1.1528787729.1528787729.1.jzqsr=ts%2Ezhaopin%2Ecom|jzqct=/jump/index_new%2Ehtml.-; rt=94d63a8488b24937a3c0fa3323171ec7; NTKF_T2D_CLIENTID=guest25D33CD9-F921-246D-C8A6-F2DA72059A77; JSSearchModel=0; LastCity%5Fid=530; LastSearchHistory=%7b%22Id%22%3a%227f365189-9ff7-434d-a4ef-7681edfd1e06%22%2c%22Name%22%3a%22%e5%ba%ad%e9%99%a2+%2b+%e5%8c%97%e4%ba%ac%22%2c%22SearchUrl%22%3a%22http%3a%2f%2fsou.zhaopin.com%2fjobs%2fsearchresult.ashx%3fjl%3d%25e5%258c%2597%25e4%25ba%25ac%26kw%3d%25e5%25ba%25ad%25e9%2599%25a2%26p%3d1%26isadv%3d0%22%2c%22SaveTime%22%3a%22%5c%2fDate(1528787852947%2b0800)%5c%2f%22%7d; adfbid=0; dywea=95841923.534891412863802940.1528787680.1528787680.1530579274.2; dywec=95841923; __utmc=269921210; __xsptplus30=30.3.1530579287.1530579287.1%231%7Cother%7Ccnt%7C121122523%7C%7C%23%23uu8ODrYxUQe5X_OBLyrIPlIi4tgz89ak%23; dywez=95841923.1530579288.2.3.dywecsr=other|dyweccn=121122523|dywecmd=cnt|dywectr=%E6%99%BA%E8%81%94%E6%8B%9B%E8%81%98; __utma=269921210.202878785.1528787680.1530579275.1530579288.3; __utmz=269921210.1530579288.3.3.utmcsr=other|utmccn=121122523|utmcmd=cnt|utmctr=%E6%99%BA%E8%81%94%E6%8B%9B%E8%81%98; Hm_lvt_38ba284938d5eddca645bb5e02a02006=1528787680,1528787778,1530579277,1530579288; sts_deviceid=1645da2b13d3ee-0f4dca6cc3db76-444a022e-1440000-1645da2b13e57; sts_sg=1; sts_sid=1645da2b141836-05f156867f509f-444a022e-1440000-1645da2b142590; zp_src_url=http%3A%2F%2Fts.zhaopin.com%2Fjump%2Findex_new.html%3Futm_source%3Dother%26utm_medium%3Dcnt%26utm_term%3D%26utm_campaign%3D121122523%26utm_provider%3Dzp%26sid%3D121122523%26site%3Du2757457.k9454548825.a14570743590.pb; ZP_OLD_FLAG=false; LastCity=%E5%8C%97%E4%BA%AC; urlfrom=121126445; urlfrom2=121126445; adfcid=none; adfcid2=none; __utmt=1; dyweb=95841923.12.10.1530579274; __utmb=269921210.11.10.1530579288; GUID=c76e127e96ea46c3bd24084a13ac02c9; Hm_lpvt_38ba284938d5eddca645bb5e02a02006=1530582224; ZL_REPORT_GLOBAL={%22sou%22:{%22actionIdFromSou%22:%22e4f06be1-a01d-4b64-9336-10bcc1163343-sou%22%2C%22funczone%22:%22smart_matching%22}}; sts_evtseq=94"
        },
        'RETRY_TIMES' : 5, # 下载器重试次数
        'DOWNLOAD_TIMEOUT' : 3, # 3秒以后请求超时
        'CONCURRENT_REQUEST' : 32,
        'ITEM_PIPELINES' : {
            'project.pipelines.MysqlPipeline' : 1,
        }
    }

    def parse(self,response):
        for i in range(0,10141,60):
        # print(response.text)
            fullurl = self.base_url % i

            req = scrapy.Request(fullurl,callback =self.parse_list)

            yield req

    def parse_list(self,response):
        # res=response.text
        res=json.loads(response.text)
        # print(type(res))
        for i in res['data']['results']:
            detail_url = i['positionURL']

            yield scrapy.Request(detail_url,callback = self.parse_detail)


    def parse_detail(self, response):
        # print(response.text)
        item = ZhiLianItem()
        # url=response.url
        # print(response.url)
        # print(response.text)
        # time.sleep(100)
        url = response.url
        pname = response.css('h1::text').extract_first()
        money = response.css('.terminal-ul strong::text').extract()[0]
        smoney = money.replace('元/月','').strip().split('-')[0]
        emoney = money.replace('元/月','').strip().split('-')[1]
        location = response.xpath('//div[6]/div[1]/ul/li[2]/strong/a/text()').extract()[0]
        year = response.xpath('//div[6]/div[1]/ul/li[5]/strong/text()').extract_first()
        syear,eyear = self.parse_year(year)
        degree = response.xpath('//div[1]/ul/li[6]/strong/text()').extract_first()
        ptype = response.xpath('//div[6]/div[1]/ul/li[4]/strong/text()').extract_first()
        tags = '智联招聘'
        date_pub = response.xpath('//span[@id="span4freshdate"]/text()').extract_first().split(' ')[0]
        advantage = response.xpath('//div[5]/div[1]/div[1]/div[1]/span/text()').extract()
        if len(advantage)>0:
            advantage = '-'.join(advantage)
        else:
            advantage = '没有福利'

        jobdesc = response.xpath('/html/body/div[6]/div[1]/div[1]/div/div[1]').css('p::text').extract()
        jobdesc = '-'.join(jobdesc).strip().replace(' ','')

        jobaddr = response.xpath('//div[6]/div[1]/div[1]/div/div[1]/h2/text()').extract()[0].strip()

        company = response.xpath('//div[5]/div[1]/div[1]/h2/a/text()').extract_first()

        crawl_time = datetime.now().strftime('%Y-%m-%d')
        # print(company)
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

        # print(year,'---',syear,eyear)
        # print(smoney,'-',emoney)



    def parse_year(self,value):
        if '-' in value:
            res = value.split('-')
            syear = res[0]
            eyear = res[1].replace('年','')

        elif '以上' in value:
            res = self.num_pattern.search(value).group()
            syear = res
            eyear = res

        else:
            syear = 0
            eyear = 0 

        return syear,eyear 


    def md5(self,value):
        m = hashlib.md5()
        m.update(bytes(value,encoding='utf-8'))
        return m.hexdigest()