# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose,TakeFirst,Join

import datetime

import GtwSpiders.utils.common as common_util
from GtwSpiders.settings import SQL_DATETIME_FORMAT

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

    def get_insert_sql(self):
        # 插入知乎question表的sql语句
        insert_sql = """
            INSERT INTO zhihu_question(zhihu_id, topics, url, title, content, answer_num, comments_num,
              watch_user_num, click_num, crawl_time, crawl_update_time
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE content=VALUES(content), answer_num=VALUES(answer_num), comments_num=VALUES(comments_num),
              watch_user_num=VALUES(watch_user_num), click_num=VALUES(click_num)
        """

        zhihu_id = self["zhihu_id"][0]
        topics = ",".join(self["topics"])
        url = self["url"][0]
        title = "".join(self["title"])

        try:
            content = "".join(self["content"])
        except BaseException:
            content = "无"

        try:
            answer_num = common_util.get_nums("".join(self["answer_num"]))
        except BaseException:
            answer_num = 0

        comments_num = common_util.get_nums("".join(self["comments_num"]))

        if len(self["watch_user_num"]) == 2:
            watch_user_num = common_util.extract_num_include_dot(self["watch_user_num"][0])
            click_num = common_util.extract_num_include_dot(self["watch_user_num"][1])
        else:
            watch_user_num = common_util.extract_num_include_dot(self["watch_user_num"][0])
            click_num = 0

        # 时间戳转时间格式
        crawl_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)
        crawl_update_time = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)

        params = (
            zhihu_id,
            topics,
            url,
            title,
            content,
            answer_num,
            comments_num,
            watch_user_num,
            click_num,
            crawl_time,
            crawl_update_time
        )

        return insert_sql, params


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

    def get_insert_sql(self):
        # 插入知乎answer表的sql语句
        insert_sql = """
            INSERT INTO zhihu_answer(zhihu_id, url, question_id, author_id, content, praise_num, comments_num,
              create_time, update_time, crawl_time,author_name, crawl_update_time
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s)
            ON DUPLICATE KEY UPDATE content=VALUES(content), comments_num=VALUES(comments_num), praise_num=VALUES(praise_num),
              update_time=VALUES(update_time), author_name=VALUES(author_name), crawl_update_time=VALUES(crawl_update_time)
        """

        # 时间戳转时间格式
        create_time = datetime.datetime.fromtimestamp(
            self["create_time"]).strftime(SQL_DATETIME_FORMAT)
        update_time = datetime.datetime.fromtimestamp(
            self["update_time"]).strftime(SQL_DATETIME_FORMAT)

        # sql参数
        params = (
            self["zhihu_id"], self["url"], self["question_id"],
            self["author_id"], self["content"], self["praise_num"],
            self["comments_num"], create_time, update_time,
            self["crawl_time"].strftime(SQL_DATETIME_FORMAT),
            self["author_name"],
            datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)
        )

        return insert_sql, params

