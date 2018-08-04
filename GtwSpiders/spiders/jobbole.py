# -*- coding: utf-8 -*-
import re
import scrapy
from scrapy.http import Request
from urllib import parse


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def parse(self, response):
        """
        获取文章列表的url,交由scrapy进行解析下载
        获取下一页url，交由scrapy解析
        """

        # 获取每页列表中文章url
        # post_urls = response.css("#archive .floated-thumb .post-thumb a::attr(href)").extract()
        post_nodes = response.css("#archive .floated-thumb .post-thumb a")
        for post_node in post_nodes:
            image_url = post_node.css("img::attr(src)").extract_first("")  # 获取封面图的url
            post_url = post_node.css("::attr(href)").extract_first("")

            # yield相当于在此处return了，代码不再向下执行了，当再次调用parse()方法时，又从yield的下一行开始执行
            # parse.urljoin的好处，如果没有域名，就从response里取出来；如果有域名则不起作用了
            # 在下载网页的时候把获取到的封面图的url，通过meta将它发送出去，最后也传给了parse_detail的response
            yield Request(url=parse.urljoin(response.url, post_url),
                          meta={"front_image_url": image_url},
                          callback=self.parse_detail)

        # 提取下一页url,交由scrapy解析下载
        next_url = response.css(".next.page-numbers::attr(href)").extract_first("")
        if next_url:
            yield Request(url=parse.urljoin(response.url, next_url), callback=self.parse)

    def parse_detail(self, response):
        """
        解析具体文章内容
        """

        # 标题
        title = response.xpath('//div[@class="entry-header"]/h1/text()').extract_first("")  # xpath获取文本内容通过./text()
        title = response.css(".entry-header h1::text").extract_first()  # css通过::text来获取文本内容

        # 创建时间
        create_date = response.css("p.entry-meta-hide-on-mobile::text").extract()[0].strip().replace("·", "").strip()

        # 点赞数
        praise_nums = response.css(".vote-post-up h10::text").extract()[0]

        # 收藏数
        fav_nums = response.css(".bookmark-btn::text").extract()[0]
        match_re = re.match(".*?(\d+).*", fav_nums)
        if match_re:
            fav_nums = int(match_re.group(1))
        else:
            fav_nums = 0

        # 评论数
        comment_nums = response.css("a[href='#article-comment'] span::text").extract()[0]
        match_re = re.match(".*?(\d+).*", comment_nums)
        if match_re:
            comment_nums = int(match_re.group(1))
        else:
            comment_nums = 0

        # 正文内容
        content = response.css("div.entry").extract()[0]

        tag_list = response.css("p.entry-meta-hide-on-mobile a::text").extract()
        tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        tags = ",".join(tag_list)

        pass
