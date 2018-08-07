# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose,TakeFirst,Join

import GtwSpiders.utils.common as common_util

# 定义Pipelines中的数据内容Item
# 数据爬取的任务就是从非结构的数据中提取出结构性的数据, Item可以让我们自定义需要的数据结构


class GtwSpidersItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


# 自定义itemloader实现默认提取第一个
class ItemFirstValueLoader(ItemLoader):
    default_output_processor = TakeFirst()


# JobBole网站对应的Item
class JobBoleItem(scrapy.Item):
    # 通过使用scrapy.Field()来获取从爬虫结果中要获取的fields, 作为当前Item的属性
    title = scrapy.Field()
    create_date = scrapy.Field(
        # input_processor是针对数组中的每个值
        # MapCompose是对值依次调用传入的方法
        input_processor=MapCompose(common_util.date_convert)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        # 图片处理的管道是按照数组进行处理的，所以对image不使用默认的output_processor
        output_processor=MapCompose(lambda value:value)
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor=MapCompose(common_util.get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(common_util.get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(common_util.get_nums)
    )
    tags = scrapy.Field(
        input_processor=MapCompose(common_util.remove_comment_tags),
        # 多标签也不是使用自定义中的output_processor，采用对数组中的值按“,”连接
        output_processor=Join(",")
    )
    content = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            INSERT INTO jobbole_article(url_object_id, title, url, front_image_url, front_image_path, `praise_nums`, `comment_nums`, `fav_nums`, `tags`, `content`, `create_date`) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        params = (
            self["url_object_id"],
            self["title"],
            self["url"],
            self["front_image_url"],
            self["front_image_path"],
            self["praise_nums"],
            self["comment_nums"],
            self["fav_nums"],
            self["tags"],
            self["content"],
            self["create_date"]
        )

        return insert_sql, params


# 知乎的问题 item
class ZhihuQuestionItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    topics = scrapy.Field()
    url = scrapy.Field()
    title = scrapy.Field()
    content = scrapy.Field()
    answer_num = scrapy.Field()
    comments_num = scrapy.Field()
    watch_user_num = scrapy.Field()
    click_num = scrapy.Field()
    crawl_time = scrapy.Field()


# 知乎的问题回答item
class ZhihuAnswerItem(scrapy.Item):
    zhihu_id = scrapy.Field()
    url = scrapy.Field()
    question_id = scrapy.Field()
    author_id = scrapy.Field()
    content = scrapy.Field()
    praise_num = scrapy.Field()
    comments_num = scrapy.Field()
    create_time = scrapy.Field()
    update_time = scrapy.Field()
    crawl_time = scrapy.Field()
    author_name = scrapy.Field()

