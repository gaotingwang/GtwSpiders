# -*- coding: utf-8 -*-

from urllib import parse

import scrapy
from scrapy.http import Request
from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals

from selenium import webdriver
import os

from GtwSpiders.items import JobBoleItem
from GtwSpiders.items import ItemFirstValueLoader
from GtwSpiders.utils.common import get_md5


class JobboleSpider(scrapy.Spider):
    name = 'jobbole'
    allowed_domains = ['blog.jobbole.com']
    start_urls = ['http://blog.jobbole.com/all-posts/']

    def __init__(self):
        # 每个spider可以有自己的browser
        # 初始化构建浏览器，这样可以使得不打开很多浏览器
        self.browser = webdriver.Chrome(executable_path=os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))) + "/tools/chromedriver")
        super(JobboleSpider, self).__init__()
        # 在当前spider关闭的时候退出浏览器
        dispatcher.connect(self.spider_close, signals.spider_closed)

    def spider_close(self, spider):
        print("spider close")
        self.browser.quit()

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

        # # 标题
        # # title = response.xpath('//div[@class="entry-header"]/h1/text()').extract_first("")  # xpath获取文本内容通过./text()
        # # extract_first('') 比 extract()[0]好，因为后者有风险，如果为空就会出错。前者如果为空默认为''
        # title = response.css(".entry-header h1::text").extract_first('')  # css通过::text来获取文本内容
        #
        # # 创建时间
        # create_date = response.css("p.entry-meta-hide-on-mobile::text").extract()[0].strip().replace("·", "").strip()
        #
        # # 文章图片
        # front_image_url = response.meta.get("front_image_url", "")
        #
        # # 点赞数
        # praise_nums = response.css(".vote-post-up h10::text").extract()[0]
        #
        # # 收藏数
        # fav_nums = response.css(".bookmark-btn::text").extract()[0]
        # match_re = re.match(".*?(\d+).*", fav_nums)
        # if match_re:
        #     fav_nums = int(match_re.group(1))
        # else:
        #     fav_nums = 0
        #
        # # 评论数
        # comment_nums = response.css("a[href='#article-comment'] span::text").extract()[0]
        # match_re = re.match(".*?(\d+).*", comment_nums)
        # if match_re:
        #     comment_nums = int(match_re.group(1))
        # else:
        #     comment_nums = 0
        #
        # # 正文内容
        # content = response.css("div.entry").extract()[0]
        #
        # tag_list = response.css("p.entry-meta-hide-on-mobile a::text").extract()
        # tag_list = [element for element in tag_list if not element.strip().endswith("评论")]
        # tags = ",".join(tag_list)
        #
        # # 填充值到Item中
        # article_item = JobBoleItem()
        # article_item["title"] = title
        # article_item["url"] = response.url
        # article_item["url_object_id"] = get_md5(response.url)
        # try:
        #     create_date = datetime.datetime.strptime(create_date, "%Y/%m/%d").date()
        # except Exception:
        #     create_date = datetime.datetime.now().date()
        # article_item["create_date"] = create_date
        # article_item["front_image_url"] = [front_image_url]  # 在图片处理时，会按照数组的形式处理，所以此处需要转数组
        # article_item["praise_nums"] = praise_nums
        # article_item["comment_nums"] = comment_nums
        # article_item["fav_nums"] = fav_nums
        # article_item["tags"] = tags
        # article_item["content"] = content

        # 通过item loader加载item
        item_loader = ItemFirstValueLoader(item=JobBoleItem(), response=response)

        front_image_url = response.meta.get("front_image_url", "")  # 文章封面图
        item_loader.add_value("front_image_url", [front_image_url]) # 图片处理的管道是按照数组进行处理的
        item_loader.add_value("url", response.url)
        item_loader.add_value("url_object_id", get_md5(response.url))
        item_loader.add_css("title", ".entry-header h1::text")
        item_loader.add_css("create_date", "p.entry-meta-hide-on-mobile::text")
        item_loader.add_css("praise_nums", ".vote-post-up h10::text")
        item_loader.add_css("comment_nums", "a[href='#article-comment'] span::text")
        item_loader.add_css("fav_nums", ".bookmark-btn::text")
        item_loader.add_css("tags", "p.entry-meta-hide-on-mobile a::text")
        item_loader.add_css("content", "div.entry")

        article_item = item_loader.load_item()
        # 返回当前的article_item，scrapy会将这些Item放入Pipelines中
        yield article_item
