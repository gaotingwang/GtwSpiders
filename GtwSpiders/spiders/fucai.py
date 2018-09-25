# -*- coding: utf-8 -*-
import scrapy
import json

from scrapy.http import Request

from items import FuCaiItem
from items import ItemFirstValueLoader


class FucaiSpider(scrapy.Spider):
    name = 'fucai'
    allowed_domains = ['www.cwl.gov.cn']
    start_urls = ['http://www.cwl.gov.cn/cwl_admin/kjxx/findDrawNotice?name=ssq&issueCount=&issueStart=&issueEnd=&dayStart=2013-01-01&dayEnd=2018-10-01&pageNo=']

    # 为了让不同的spider应用不同的设置，可以在spider代码中加入custom_settings进行个性化设置。
    custom_settings = {
        "COOKIES_ENABLED": False,
        "DOWNLOAD_DELAY": 1,
        # 请求头设置，也可以在setting.py中设置DEFAULT_REQUEST_HEADERS
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Connection': 'keep-alive',
            'Host': 'www.cwl.gov.cn',
            'Referer': 'http://www.cwl.gov.cn/kjxx/ssq/kjgg/',
        }
    }

    def parse(self, response):
        result_dict = json.loads(response.text)
        if result_dict["result"]:

            url = response.request.url
            flag = 'pageNo='
            flag_index = url.index(flag)
            # 计算下一页地址
            base_url = url[ : flag_index+len(flag)]
            new_page = url[flag_index+len(flag) : ]
            if new_page:
                new_page = int(url[flag_index+len(flag) : ])
                new_page += 1
            else:
                new_page = 1

            yield Request(url=base_url + str(new_page), callback=self.parse_detail)

    def parse_detail(self, response):
        """
        解析每页双色球彩票数据
        """
        for result in json.loads(response.text)["result"]:
            # print('>>>', result['code'] + '期的双色球')
            # print('日期为:', result['date'][:-3])
            # print('星期' + result['week'])
            # print('红球号码为:', result['red'])
            # print('蓝球号码为:', result['blue'])
            # print('蓝2号码为:', result['blue2'])
            # print()

            fucai_item = FuCaiItem()
            fucai_item["code"] = result['code']
            fucai_item["date"] = result['date'][:-3]
            fucai_item["week"] = '星期' + result['week']
            fucai_item["red"] = result['red']
            fucai_item["blue"] = result['blue']

            # item_loader = ItemFirstValueLoader(item=FuCaiItem(), response=response)
            # item_loader.add_value("code", result['code'])
            # item_loader.add_value("date", result['date'][:-3])
            # item_loader.add_value("week", '星期' + result['week'])
            # item_loader.add_value("red", result['red'])
            # item_loader.add_value("blue", result['blue'])
            # fucai_item = item_loader.load_item()

            yield fucai_item