# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

# 定义了数据不同的处理管道

from scrapy.pipelines.images import ImagesPipeline
from scrapy.exporters import JsonItemExporter

import codecs
import json


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

