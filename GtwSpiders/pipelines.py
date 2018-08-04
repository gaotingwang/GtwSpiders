# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

# 定义了数据不同的处理管道

from scrapy.pipelines.images import ImagesPipeline


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

        return item
