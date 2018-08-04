# -*- coding: utf-8 -*-

import hashlib


def get_md5(target):
    """
    md5 加密
    """

    if isinstance(target, str):
        target = target.encode("utf-8")
    md5 = hashlib.md5()
    md5.update(target)
    return md5.hexdigest()

