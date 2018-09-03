# _*_ coding: utf-8 _*_

from elasticsearch_dsl import Document, Date, Integer, Keyword, Text, connections, Completion, analyzer

# 使用参考地址 https://github.com/elastic/elasticsearch-dsl-py

# 定义与es服务器连接，连接地址允许有多个
connections.create_connection(hosts=["localhost"])

my_analyzer = analyzer('ik_max_word')

class ArticleType(Document):
    # 使用搜索建议，必须添加suggest属性，type为completion
    suggest = Completion(analyzer=my_analyzer) # 此处需要指定自己定义analyzer
    # 伯乐在线文章类型
    title = Text(analyzer="ik_max_word")
    create_date = Date()
    url = Keyword()
    url_object_id = Keyword()
    front_image_url = Keyword()
    front_image_path = Keyword()
    praise_nums = Integer()
    comment_nums = Integer()
    fav_nums = Integer()
    tags = Text(analyzer="ik_max_word")
    content = Text(analyzer="ik_smart")
    crawl_time = Date()

    # 定义了es中对应的index
    class Index:
        name = 'jobbole' # index
        doc_type = "article"
        # settings = {
        #     "number_of_shards": 2,
        # }

    class Meta:
        doc_type = "article"


if __name__ == "__main__":
    ArticleType.init()
