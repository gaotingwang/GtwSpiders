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

# 过滤掉评论中不需要的标签
def remove_comment_tags(tag_value):
    if "评论" in tag_value:
        return ""
    else:
        return tag_value

