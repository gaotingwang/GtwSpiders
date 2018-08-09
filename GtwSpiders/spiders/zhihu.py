# -*- coding: utf-8 -*-
import scrapy
from scrapy.loader import ItemLoader

import time
from datetime import datetime
import re
import base64
import hmac
import hashlib
import json
from PIL import Image
from urllib import parse

from GtwSpiders.items import ZhihuQuestionItem,ZhihuAnswerItem


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

    # question第一页answer的请求url
    start_answer_url = "https://www.zhihu.com/api/v4/questions/{0}/answers?sort_by=default&include=data%5B%2A%5D.is_normal%2Cis_sticky%2Ccollapsed_by%2Csuggest_edit%2Ccomment_count%2Ccollapsed_counts%2Creviewing_comments_count%2Ccan_comment%2Ccontent%2Ceditable_content%2Cvoteup_count%2Creshipment_settings%2Ccomment_permission%2Cmark_infos%2Ccreated_time%2Cupdated_time%2Crelationship.is_author%2Cvoting%2Cis_thanked%2Cis_nothelp%2Cupvoted_followees%3Bdata%5B%2A%5D.author.is_blocking%2Cis_blocked%2Cis_followed%2Cvoteup_count%2Cmessage_thread_token%2Cbadge%5B%3F%28type%3Dbest_answerer%29%5D.topics&limit={1}&offset={2}"

    # 登录知乎的用户名密码
    username = 'username'
    password = 'password'

    # 登录所需要的头信息
    zhihu_source = 'com.zhihu.web'
    zhihu_grant_type = 'password'
    captcha = ''
    client_id = 'c3cef7c66a1843f8b3a9e6a1e3160e20'
    headers = {
        'Authorization': 'oauth ' + client_id,
        'Host': 'www.zhihu.com',
        'Origin': 'https://www.zhihu.com',
        'Referer': 'https://www.zhihu.com/signup?next=%2F',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)Chrome/63.0.3239.84 Safari/537.36'
    }

    def parse(self, response):
        """
        总体是深度优先的思想，向下去遍历提问以及回答，之后去遍历另一节点
        :param response:
        :return:
        """
        # 提取出html页面中的所有url，并跟踪这些url进一步爬取。
        # 如果提取的url中格式为/question/xxx 就下载之后直接进入解析函数
        all_urls = response.css("a::attr(href)").extract()
        all_urls = [parse.urljoin(response.url, url) for url in all_urls]
        # 使用lambda函数对于每一个url进行过滤，如果是true放回列表，返回false去除。
        all_urls = filter(lambda x: True if x.startswith("https") else False, all_urls)

        for url in all_urls:
            # 具体问题以及具体答案的url我们都要提取出来，或关系
            match_obj = re.match("(.*zhihu.com/question/\d+)(/|$).*", url)
            if match_obj:
                # 如果提取到question相关的页面则下载后交由提取函数进行提取
                request_url = match_obj.group(1)
                yield scrapy.Request(request_url, headers=self.headers, callback=self.parse_question)
                # break  # 方便调试此处可以直接break
            else:
                # pass
                # 方便调试此处可以注释掉,只爬取几个提问页面
                # 如果不是question页面则直接进一步跟踪
                yield scrapy.Request(url, headers=self.headers)

    # 获取提问内容
    def parse_question(self, response):
        # 从response.url中提取出question_id
        match_obj = re.match("(.*zhihu.com/question/(\d+))(/|$).*", response.url)
        if match_obj:
            question_id = int(match_obj.group(2))

        item_loader = ItemLoader(item=ZhihuQuestionItem(), response=response)
        item_loader.add_value("zhihu_id", question_id)
        item_loader.add_css("title", "h1.QuestionHeader-title::text")
        item_loader.add_css("content",".QuestionHeader-detail")
        item_loader.add_value("url", response.url)
        item_loader.add_css("answer_num", ".List-headerText span::text")
        item_loader.add_css("comments_num", ".QuestionHeader-Comment button::text")
        item_loader.add_css("watch_user_num", ".NumberBoard-itemValue ::text")  # 这里一次把一列值提出来
        item_loader.add_css("topics", ".QuestionHeader-topics .Tag.QuestionTopic .Popover div::text")

        question_item = item_loader.load_item()

        # 方便调试，可以分别注释掉下面一个
        yield question_item
        # 查找对应的回答页面
        yield scrapy.Request(self.start_answer_url.format(question_id, 20, 0), headers=self.headers, callback=self.parse_answer)

        # 可选：在question页面也进行进一步的a标签获取提问页面地址进行跟踪

    # 获取回答内容
    def parse_answer(self, reponse):
        # 处理question的answer
        ans_json = json.loads(reponse.text)
        is_end = ans_json["paging"]["is_end"]
        next_url = ans_json["paging"]["next"]

        # 提取answer的具体字段
        for answer in ans_json["data"]:
            answer_item = ZhihuAnswerItem()
            answer_item["zhihu_id"] = answer["id"]
            answer_item["url"] = answer["url"]
            answer_item["question_id"] = answer["question"]["id"]
            answer_item["author_id"] = answer["author"]["id"] if "id" in answer["author"] else None
            answer_item["author_name"] = answer["author"]["name"] if "name" in answer["author"] else None
            answer_item["content"] = answer["content"] if "content" in answer else None
            answer_item["praise_num"] = answer["voteup_count"]
            answer_item["comments_num"] = answer["comment_count"]
            answer_item["create_time"] = answer["created_time"]
            answer_item["update_time"] = answer["updated_time"]
            answer_item["crawl_time"] = datetime.now()

            yield answer_item

        # 如果还有下一页，继续获取下一页的回答内容
        if not is_end:
            yield scrapy.Request(next_url, headers=self.headers, callback=self.parse_answer)

    # 因为知乎需要先进行登录，所以重写它的start_requests
    def start_requests(self):
        # 先访问登录接口，判断是否需要验证码，根据结果执行callback
        return [scrapy.Request(
                'https://www.zhihu.com/api/v3/oauth/captcha?lang=en',
                headers=self.headers,
                callback=self.need_captcha)]

    # 判断是否需要验证码
    def need_captcha(self, response):
        captcha_info = json.loads(response.text)
        print("是否需要验证码：", captcha_info['show_captcha'])
        if captcha_info['show_captcha']:
            # 获取验证码内容
            return [scrapy.Request(
                'https://www.zhihu.com/api/v3/oauth/captcha?lang=en',
                headers=self.headers,
                method="PUT",
                dont_filter=True,
                callback=self.do_captcha)]
        else:
            self.login(response)

    # 获取验证码图片
    def do_captcha(self, response):
        img_base64 = re.findall(
            r'"img_base64":"(.+)"', response.text, re.S)[0].replace(r'\n', '')
        with open('./captcha.jpg', 'wb') as f:
            f.write(base64.b64decode(img_base64))
        img = Image.open('./captcha.jpg')
        img.show()
        capt = input('请输入图片里的验证码：')
        # 这里必须先把参数 POST 到验证码接口
        self.captcha = capt
        return [scrapy.FormRequest('https://www.zhihu.com/api/v3/oauth/captcha?lang=en',
                                   headers=self.headers,
                                   formdata={'input_text': capt},
                                   callback=self.login)]

    # 执行登录
    def login(self, response):
        response_info = json.loads(response.text)
        # 不需要验证码或验证码验证正确
        if (response_info.get('show_captcha') is not None and not response_info.get('show_captcha')) or response_info['success']:
            login_url = 'https://www.zhihu.com/api/v3/oauth/sign_in'
            # 登录表单的签名和时间戳
            timestamp = int(time.time() * 1000)
            signature = self._get_signature(timestamp)
            params = {
                'client_id': self.client_id,
                'grant_type': self.zhihu_grant_type,
                'timestamp': str(timestamp),
                'source': self.zhihu_source,
                'signature': signature,
                'username': self.username,
                'password': self.password,
                'captcha': self.captcha,
                'lang': 'en',
                'ref_source': 'homepage',
                'utm_source': ''
            }
            # 表单请求登录
            yield scrapy.FormRequest(login_url, headers=self.headers, formdata=params, callback=self.do_you_want)
        else:
            print("验证码错误：" + response.text)

    # 根据登录之后的返回信息，干你想干的
    def do_you_want(self, response):
        # 验证服务器返回是否成功。
        if 'error' in response.text:
            print(re.findall(r'"message":"(.+?)"', response.text)[0])

        login_message = json.loads(response.text)
        # 根据登录成功后返回的Oauth2信息，更新头信息
        self.headers.update({
            'Authorization': login_message.get('token_type') + ' ' + login_message.get('access_token'),
            'cookie': login_message.get('cookie'),
            'uid': login_message.get('uid'),
            'user_id': login_message.get('user_id'),
        })
        print("登录成功")

        # 登录成功后访问start_urls中的地址
        for url in self.start_urls:
            # 原方法中调用make_requests_from_url()，因为Request没有传递headers参数，所以舍弃重写
            # yield self.make_requests_from_url(url)
            # 如果没有回调函数，默认之后调用parse()方法
            yield scrapy.Request(url, dont_filter=True, headers=self.headers)

    def _get_signature(self, timestamp):
        """
            通过 Hmac 算法计算返回签名,实际是几个固定字符串加时间戳
        """
        ha = hmac.new(b'd1b964811afb40118a12068ff74a12f4', digestmod=hashlib.sha1)
        ha.update(bytes((self.zhihu_grant_type + self.client_id + self.zhihu_source + str(timestamp)), 'utf-8'))
        return ha.hexdigest()