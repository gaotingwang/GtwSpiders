# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import datetime
import re

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose,TakeFirst,Join

# 定义Pipelines中的数据内容Item,
# 数据爬取的任务就是从非结构的数据中提取出结构性的数据, Item可以让我们自定义需要的数据结构


# 字符串日期转日期格式
def date_convert(date_str):
    date_str = date_str.replace("\r","").replace("\n","").replace(" ·","").strip()
    try:
        create_date = datetime.datetime.strptime(date_str.replace("\r","").replace("\n","").replace(" ·","").strip(), "%Y/%m/%d").date()
    except Exception:
        create_date = datetime.datetime.now().date()

    return create_date

# 正则方式获取字符串中的数字
def get_nums(value):
    match_re = re.match(".*?(\d+).*", value)
    if match_re:
        nums = int(match_re.group(1))
    else:
        nums = 0
    return nums

# 过滤掉评论中不需要的标签
def remove_comment_tags(tag_value):
    if "评论" in tag_value:
        return ""
    else:
        return tag_value


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
        input_processor=MapCompose(date_convert)
    )
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    front_image_url = scrapy.Field(
        # 图片处理的管道是按照数组进行处理的，所以对image不使用默认的output_processor
        output_processor=MapCompose(lambda value:value)
    )
    front_image_path = scrapy.Field()
    praise_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    comment_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    fav_nums = scrapy.Field(
        input_processor=MapCompose(get_nums)
    )
    tags = scrapy.Field(
        input_processor=MapCompose(remove_comment_tags),
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
