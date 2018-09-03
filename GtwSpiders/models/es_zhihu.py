# _*_ coding: utf-8 _*_


from elasticsearch_dsl import Document, Date, Completion, Keyword, Text, Integer, connections, analyzer

# 使用参考地址 https://github.com/elastic/elasticsearch-dsl-py

# 定义与es服务器连接，连接地址允许有多个
connections.create_connection(hosts=["localhost"])

ik_analyzer = analyzer('ik_max_word')


class ZhiHuQuestionType(Document):
    suggest = Completion(analyzer=ik_analyzer)
    # 知乎的问题 item
    zhihu_id = Keyword()
    topics = Text(analyzer="ik_max_word")
    url = Keyword()
    title = Text(analyzer="ik_max_word")
    content = Text(analyzer="ik_max_word")
    answer_num = Integer()
    comments_num = Integer()
    watch_user_num = Integer()
    click_num = Integer()
    crawl_time = Date()

    # 定义了es中对应的index
    class Index:
        name = 'zhihu'
        doc_type = "question"

    class Meta:
        doc_type = "question"


class ZhiHuAnswerType(Document):
    suggest = Completion(analyzer=ik_analyzer)
    # 知乎的问题 item
    zhihu_id = Keyword()
    url = Keyword()
    question_id = Keyword()
    author_id = Keyword()
    content = Text(analyzer="ik_max_word")
    praise_num = Integer()
    comments_num = Integer()
    create_time = Date()
    update_time = Date()
    crawl_time = Date()
    author_name = Keyword()

    # 定义了es中对应的index
    class Index:
        name = 'zhihu'
        doc_type = "answer"

    class Meta:
        doc_type = "answer"


if __name__ == "__main__":
    ZhiHuQuestionType.init()
    ZhiHuAnswerType.init()
