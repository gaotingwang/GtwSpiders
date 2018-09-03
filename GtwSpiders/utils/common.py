# -*- coding: utf-8 -*-

import hashlib
import datetime
import re


def get_md5(target):
    """
    md5 加密
    """

    if isinstance(target, str):
        target = target.encode("utf-8")
    md5 = hashlib.md5()
    md5.update(target)
    return md5.hexdigest()

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

# 从包含,的字符串中提取出数字
def extract_num_include_dot(text):
    text_num = text.replace(',', '')
    try:
        nums = int(text_num)
    except:
        nums = -1
    return nums

# 过滤掉评论中不需要的标签
def remove_comment_tags(tag_value):
    if "评论" in tag_value:
        return ""
    else:
        return tag_value

# 去掉工作城市的斜线
def remove_splash(value):
    return value.replace("/", "")

# 处理具体的工作地址信息
def handle_jobaddr(value):
    addr_list = value.split("\n")
    addr_list = [item.strip() for item in addr_list if item.strip() != "查看地图"]
    return "".join(addr_list)

# 生成es搜索建议词
def generate_suggests(es_connection, index, info_tuple):
    es = es_connection
    # 根据字符串，生成搜索建议数组
    used_words = set()
    suggests = []
    for text, weight in info_tuple:
        if text:
            # 调用es接口analyzer分析字符串
            words = es.indices.analyze(index=index, body={"analyzer": "ik_max_word", "text": "{0}".format(text)})
            # 去掉分析出来的重复词
            analyzed_words = set([r["token"] for r in words["tokens"] if len(r["token"]) > 1])
            # 过滤掉之前已有的词
            new_words = analyzed_words - used_words
            used_words = used_words | new_words
        else:
            new_words = set()

        if new_words:
            suggests.append({"input": list(new_words), "weight": weight})

    return suggests
