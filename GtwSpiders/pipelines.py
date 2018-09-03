# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

# 定义了数据不同的处理管道

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter
from twisted.enterprise import adbapi

import codecs
import json
import MySQLdb
import MySQLdb.cursors

class GtwspidersPipeline(object):
    def process_item(self, item, spider):
        return item


# 此管道在setting.py中配置的优先级高，会先执行
class ArticleImagePipeline(ImagesPipeline):
    """
        继承ImagesPipeline，定制自己的图片处理管道
    """

    # 重写该方法可从result中获取到图片的实际下载地址
    def item_completed(self, results, item, info):
        if "front_image_url" in item:
            image_file_path = ''
            for ok, value in results:
                image_file_path = value["path"]
            item["front_image_path"] = image_file_path  # 指定图片最后的保存地址

        # 一定要将item return出去，因为下一个pipeline需要
        return item


# 自定义json文件的导出
class JsonWithEncodingPipeline(object):

    def __init__(self):
        # 使用codecs打开文件避免一些编码问题
        self.file = codecs.open('article1.json', 'w', encoding="utf-8")

    def process_item(self, item, spider):
        # 需要将item转为dict形式，指定ensure_ascii=False否则中文乱码
        lines = json.dumps(dict(item), ensure_ascii=False) + "\n"
        self.file.write(lines)
        return item

    def spider_closed(self, spider):
        self.file.close()


# 调用scrapy提供的json export导出json文件
class JsonExporterPipeline(object):

    def __init__(self):
        self.file = open('article2.json', 'wb')
        # 使用JsonItemExporter的exporter
        self.exporter = JsonItemExporter(self.file, encoding="utf-8", ensure_ascii=False)
        # 开始item导出
        self.exporter.start_exporting()

    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item

    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()


# 采用同步的机制写入mysql
class MysqlPipeline(object):

    def __init__(self):
        self.conn = MySQLdb.connect('127.0.0.1', 'root', 'root', 'scrapy-spider', charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        insert_sql = """
            INSERT INTO jobbole_article(url_object_id, title, url, front_image_url, front_image_path, `praise_nums`, `comment_nums`, `fav_nums`, `tags`, `content`, `create_date`)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s);
        """

        # 执行sql语句
        self.cursor.execute(insert_sql, (item["url_object_id"], item["title"], item["url"], item["front_image_url"], item["front_image_path"], item["praise_nums"], item["comment_nums"], item["fav_nums"], item["tags"], item["content"], item["create_date"]))
        # 事务提交
        self.conn.commit()

        return item


# 因为爬取速度可能大于数据库存储的速度，所以需要异步操作。
class MysqlTwistedPipeline(object):
    def __init__(self, dbpool):
        self.dbpool = dbpool

    @classmethod
    def from_settings(cls, settings):
        dbparms = dict(
            host = settings["MYSQL_HOST"],
            db = settings["MYSQL_DBNAME"],
            user = settings["MYSQL_USER"],
            passwd = settings["MYSQL_PASSWORD"],
            charset = 'utf8',
            cursorclass = MySQLdb.cursors.DictCursor,
            use_unicode = True,
        )
        dbpool = adbapi.ConnectionPool("MySQLdb", **dbparms)

        return cls(dbpool)

    def process_item(self, item, spider):
        # 使用twisted将mysql插入变成异步执行
        query = self.dbpool.runInteraction(self.do_insert, item)
        # 处理异常
        query.addErrback(self.handle_error, item, spider)
        return item

    def do_insert(self, cursor, item):
        # 执行具体的插入
        # 根据不同的item 构建不同的sql语句并插入到mysql中
        insert_sql, param = item.get_insert_sql()
        cursor.execute(insert_sql, param)

    def handle_error(self, failure, item, spider):
        # 处理异步插入的异常
        print (failure)

class ElasticSearchPipeline(object):
    # 将线数据写入到es中
    def process_item(self, item, spider):
        item.save_to_es()
        return item