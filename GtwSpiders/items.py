# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose,TakeFirst,Join

import datetime
import re
from w3lib.html import remove_tags
from elasticsearch_dsl import connections

import redis

import utils.common as common_util
from settings import SQL_DATETIME_FORMAT
from models.es_jobbole import ArticleType
from models.es_lagou import LagouType
from models.es_zhihu import ZhiHuQuestionType, ZhiHuAnswerType

# 与ElasticSearch进行连接,生成搜索建议
es_connection = connections.create_connection(ArticleType)

redis_cli = redis.StrictRedis(host="localhost")

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

    def clean_data(self):
        pass

    def get_insert_sql(self):
        self.clean_data()
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

    def save_to_es(self):
        # 将item转换为es数据。
        self.clean_data()
        blog = ArticleType()
        blog.title = self['title']
        blog.create_date = self["create_date"]
        blog.content = remove_tags(self["content"])
        blog.front_image_url = self["front_image_url"]
        blog.praise_nums = self["praise_nums"]
        blog.fav_nums = self["fav_nums"]
        blog.comment_nums = self["comment_nums"]
        blog.url = self["url"]
        blog.tags = self["tags"]
        blog.meta.id = self["url_object_id"]
        # 生成搜索建议词, 在保存数据时必须传入suggest
        blog.suggest = common_util.generate_suggests(es_connection,
                                                     ArticleType._default_index(),
                                                     ((blog.title, 10), (blog.tags, 6), (blog.content, 4)))
        blog.save()

        redis_cli.incr("jobbole_blog_count") # redis记录数+1

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

    def clean_data(self):
        self["question_id"] = self["question_id"][0]
        self["topics"] = ",".join(self["topics"])
        self["url"] = self["url"][0]
        self["title"] = "".join(self["title"])
        try:
            self["content"] = "".join(self["content"])
            self["content"] = remove_tags(self["content"])
        except BaseException:
            self["content"] = "无"
        try:
            self["answer_num"] = common_util.get_nums("".join(self["answer_num"]))
        except BaseException:
            self["answer_num"] = 0
        self["comments_num"] = common_util.get_nums("".join(self["comments_num"]))

        if len(self["watch_user_num"]) == 2:
            watch_user_num_click = self["watch_user_num"]
            self["watch_user_num"] = common_util.extract_num_include_dot(watch_user_num_click[0])
            self["click_num"] = common_util.extract_num_include_dot(watch_user_num_click[1])
        else:
            watch_user_num_click = self["watch_user_num"]
            self["watch_user_num"] = common_util.extract_num_include_dot(watch_user_num_click[0])
            self["click_num"] = 0

        self["crawl_time"] = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)
        self["crawl_update_time"] = datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)

    def get_insert_sql(self):
        self.clean_data()
        # 插入知乎question表的sql语句
        insert_sql = """
            INSERT INTO zhihu_question(zhihu_id, topics, url, title, content, answer_num, comments_num,
              watch_user_num, click_num, crawl_time, crawl_update_time
            )
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE content=VALUES(content), answer_num=VALUES(answer_num), comments_num=VALUES(comments_num),
              watch_user_num=VALUES(watch_user_num), click_num=VALUES(click_num)
        """

        params = (
            self["zhihu_id"],
            self["topics"],
            self["url"],
            self["title"],
            self["content"],
            self["answer_num"],
            self["comments_num"],
            self["watch_user_num"],
            self["click_num"],
            self["crawl_time"],
            self["crawl_update_time"]
        )

        return insert_sql, params

    def save_to_es(self):
        self.clean_data()
        zhihu = ZhiHuQuestionType()
        zhihu.meta.id = self["url_object_id"]
        zhihu.question_id = self["question_id"]
        zhihu.title = self["title"]
        zhihu.content = self["content"]
        zhihu.topics = self["topics"]

        zhihu.answer_num = self["answer_num"]
        zhihu.comments_num = self["comments_num"]
        zhihu.watch_user_num = self["watch_user_num"]
        zhihu.click_num = self["click_num"]
        zhihu.url = self["url"]

        zhihu.crawl_time = self["crawl_time"]

        # 在保存数据时便传入suggest
        zhihu.suggest = common_util.generate_suggests(es_connection,
                                                      ZhiHuQuestionType._default_index(),
                                                      ((zhihu.title, 10), (zhihu.topics, 7), (zhihu.content, 5)))

        zhihu.save()

        redis_cli.incr("zhihu_question_count") # redis记录数+1


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

    def clean_data(self):
        # 时间戳转时间格式
        self["create_time"] = datetime.datetime.fromtimestamp(
            self["create_time"]).strftime(SQL_DATETIME_FORMAT)
        self["update_time"] = datetime.datetime.fromtimestamp(
            self["update_time"]).strftime(SQL_DATETIME_FORMAT)
        self["crawl_time"] = self["crawl_time"].strftime(SQL_DATETIME_FORMAT)
        self["content"] = remove_tags(self["content"])

    def get_insert_sql(self):
        self.clean_data()
        # 插入知乎answer表的sql语句
        insert_sql = """
            INSERT INTO zhihu_answer(zhihu_id, url, question_id, author_id, content, praise_num, comments_num,
              create_time, update_time, crawl_time,author_name, crawl_update_time
            ) 
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,%s, %s)
            ON DUPLICATE KEY UPDATE content=VALUES(content), comments_num=VALUES(comments_num), praise_num=VALUES(praise_num),
              update_time=VALUES(update_time), author_name=VALUES(author_name), crawl_update_time=VALUES(crawl_update_time)
        """

        # sql参数
        params = (
            self["zhihu_id"], self["url"], self["question_id"],
            self["author_id"], self["content"], self["praise_num"],
            self["comments_num"], self["create_time"], self["update_time"],
            self["crawl_time"],
            self["author_name"],
            datetime.datetime.now().strftime(SQL_DATETIME_FORMAT)
        )

        return insert_sql, params

    def save_to_es(self):
        self.clean_data()
        zhihu = ZhiHuAnswerType()

        zhihu.meta.id = self["url_object_id"]
        zhihu.answer_id = self["answer_id"]
        zhihu.question_id = self["question_id"]
        zhihu.author_id = self["author_id"]
        zhihu.author_name = self["author_name"]

        zhihu.content = self["content"]
        zhihu.praise_num = self["praise_num"]
        zhihu.comments_num = self["comments_num"]
        zhihu.url = self["url"]
        zhihu.create_time = self["create_time"]

        zhihu.update_time = self["update_time"]
        zhihu.crawl_time = self["crawl_time"]

        # 在保存数据时便传入suggest
        zhihu.suggest = common_util.generate_suggests(es_connection,
                                                      ZhiHuAnswerType._default_index(),
                                                      ((zhihu.author_name, 10), (zhihu.content, 7)))
        zhihu.save()

        redis_cli.incr("zhihu_answer_count") # redis记录数+1


class LagouJobItem(scrapy.Item):
    # 拉勾网职位信息
    title = scrapy.Field()
    url = scrapy.Field()
    url_object_id = scrapy.Field()
    salary_min = scrapy.Field()
    salary_max = scrapy.Field()
    job_city = scrapy.Field(
        input_processor=MapCompose(common_util.remove_splash),
    )
    work_years_min = scrapy.Field(
        input_processor=MapCompose(common_util.remove_splash),
    )
    work_years_max = scrapy.Field(
        input_processor=MapCompose(common_util.remove_splash),
    )
    degree_need = scrapy.Field(
        input_processor=MapCompose(common_util.remove_splash),
    )
    job_type = scrapy.Field()
    publish_time = scrapy.Field()
    job_advantage = scrapy.Field()
    job_desc = scrapy.Field()
    job_addr = scrapy.Field(
        input_processor=MapCompose(remove_tags, common_util.handle_jobaddr),
    )
    company_name = scrapy.Field()
    company_url = scrapy.Field()
    tags = scrapy.Field(
        input_processor=Join(",")
    )
    crawl_time = scrapy.Field()
    crawl_update_time = scrapy.Field()

    def clean_data(self):
        match_obj1 = re.match("经验(\d+)-(\d+)年", self['work_years_min'])
        match_obj2 = re.match("经验应届毕业生", self['work_years_min'])
        match_obj3 = re.match("经验不限", self['work_years_min'])
        match_obj4 = re.match("经验(\d+)年以下", self['work_years_min'])
        match_obj5 = re.match("经验(\d+)年以上", self['work_years_min'])

        if match_obj1:
            self['work_years_min'] = match_obj1.group(1)
            self['work_years_max'] = match_obj1.group(2)
        elif match_obj2:
            self['work_years_min'] = 0.5
            self['work_years_max'] = 0.5
        elif match_obj3:
            self['work_years_min'] = 0
            self['work_years_max'] = 0
        elif match_obj4:
            self['work_years_min'] = 0
            self['work_years_max'] = match_obj4.group(1)
        elif match_obj5:
            self['work_years_min'] = match_obj4.group(1)
            self['work_years_max'] = match_obj4.group(1) + 100
        else:
            self['work_years_min'] = 999
            self['work_years_max'] = 999

        match_salary = re.match("(\d+)[Kk]-(\d+)[Kk]", self['salary_min'])
        if match_salary:
            self['salary_min'] = match_salary.group(1)
            self['salary_max'] = match_salary.group(2)
        else:
            self['salary_min'] = 666
            self['salary_max'] = 666
        match_time1 = re.match("(\d+):(\d+).*", self["publish_time"])
        match_time2 = re.match("(\d+)天前.*", self["publish_time"])
        match_time3 = re.match("(\d+)-(\d+)-(\d+)", self["publish_time"])
        if match_time1:
            today = datetime.datetime.now()
            hour = int(match_time1.group(1))
            minutues = int(match_time1.group(2))
            time = datetime.datetime(
                today.year, today.month, today.day, hour, minutues)
            self["publish_time"] = time.strftime(SQL_DATETIME_FORMAT)
        elif match_time2:
            days_ago = int(match_time2.group(1))
            today = datetime.datetime.now() - datetime.timedelta(days=days_ago)
            self["publish_time"] = today.strftime(SQL_DATETIME_FORMAT)
        elif match_time3:
            year = int(match_time3.group(1))
            month = int(match_time3.group(2))
            day = int(match_time3.group(3))
            today = datetime.datetime(year, month, day)
            self["publish_time"] = today.strftime(SQL_DATETIME_FORMAT)
        else:
            self["publish_time"] = datetime.datetime.now(
            ).strftime(SQL_DATETIME_FORMAT)
        self["crawl_time"] = self["crawl_time"].strftime(SQL_DATETIME_FORMAT)
        self["job_desc"] = remove_tags(self["job_desc"]).strip().replace("\r\n", "").replace("\t", "")

    def get_insert_sql(self):
        self.clean_data()
        insert_sql = """
            insert into lagou_job(title, url, url_object_id, salary_min, salary_max, job_city, work_years_min, work_years_max, degree_need,
            job_type, publish_time, job_advantage, job_desc, job_addr, company_name, company_url,
            tags, crawl_time) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE salary_min=VALUES(salary_min), salary_max=VALUES(salary_max), job_desc=VALUES(job_desc)
        """
        params = (
            self["title"],
            self["url"],
            self["url_object_id"],
            self["salary_min"],
            self["salary_max"],
            self["job_city"],
            self["work_years_min"],
            self["work_years_max"],
            self["degree_need"],
            self["job_type"],
            self["publish_time"],
            self["job_advantage"],
            self["job_desc"],
            self["job_addr"],
            self["company_name"],
            self["company_url"],
            self["tags"],
            self["crawl_time"],
        )

        return insert_sql, params

    def save_to_es(self):
        self.clean_data()
        job = LagouType()
        job.title = self["title"]
        job.url = self["url"]
        job.meta.id = self["url_object_id"]
        job.salary_min = self["salary_min"]
        job.salary_max = self["salary_max"]
        job.job_city = self["job_city"]
        job.work_years_min = self["work_years_min"]
        job.work_years_max = self["work_years_max"]
        job.degree_need = self["degree_need"]
        job.job_desc = self["job_desc"]
        job.job_advantage = self["job_advantage"]
        job.tags = self["tags"]
        job.job_type = self["job_type"]
        job.publish_time = self["publish_time"]
        job.job_addr = self["job_addr"]
        job.company_name = self["company_name"]
        job.company_url = self["company_url"]
        job.crawl_time = self['crawl_time']

        job.suggest = common_util.generate_suggests(es_connection,
                                                    LagouType._default_index(),
                                                    ((job.title, 10), (job.tags, 7),
                                                     (job.job_advantage, 6), (job.job_desc, 3),
                                                     (job.job_addr, 5), (job.company_name, 8),
                                                     (job.degree_need, 4),(job.job_city, 9)))
        job.save()

        redis_cli.incr("lagou_job_count") # redis记录数+1


class FuCaiItem(scrapy.Item):
    code = scrapy.Field()
    date = scrapy.Field()
    week = scrapy.Field()
    red = scrapy.Field()
    blue = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = """
            insert into fucai_double(code, publish_date, week, red, blue) VALUES (%s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE publish_date=VALUES(publish_date), red=VALUES(red), blue=VALUES(blue)
        """
        params = (
            self["code"],
            self["date"],
            self["week"],
            self["red"],
            self["blue"],
        )

        return insert_sql, params
