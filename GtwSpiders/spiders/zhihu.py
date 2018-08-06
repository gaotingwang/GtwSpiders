# -*- coding: utf-8 -*-
import scrapy
import time
import re
import base64
import hmac
import hashlib
import json
from PIL import Image


class ZhihuSpider(scrapy.Spider):
    name = 'zhihu'
    allowed_domains = ['www.zhihu.com']
    start_urls = ['http://www.zhihu.com/']

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
        pass

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