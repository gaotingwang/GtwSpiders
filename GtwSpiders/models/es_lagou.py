# _*_ coding: utf-8 _*_


from elasticsearch_dsl import Document, Date, analyzer, Completion, Keyword, Text, Integer, connections


# 使用参考地址 https://github.com/elastic/elasticsearch-dsl-py

# 定义与es服务器连接，连接地址允许有多个
connections.create_connection(hosts=["localhost"])

ik_analyzer = analyzer('ik_smart')

class LagouType(Document):
    suggest = Completion(analyzer=ik_analyzer)
    title = Text(analyzer="ik_max_word")
    url = Keyword()
    url_object_id = Keyword()
    salary_min = Integer()
    salary_max = Integer()
    job_city = Keyword()
    work_years_min = Integer()
    work_years_max = Integer()
    degree_need = Text(analyzer="ik_max_word")
    job_type = Keyword()
    publish_time = Date()
    job_advantage = Text(analyzer="ik_max_word")
    job_desc = Text(analyzer="ik_max_word")
    job_addr = Text(analyzer="ik_max_word")
    company_name = Keyword()
    company_url = Keyword()
    tags = Text(analyzer="ik_max_word")
    crawl_time = Date()

    # 定义了es中对应的index
    class Index:
        name = 'lagou'
        doc_type = "job"

    class Meta:
        doc_type = "job"


if __name__ == "__main__":
    LagouType.init()
