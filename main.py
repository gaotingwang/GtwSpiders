# -*- coding: utf-8 -*-

# 此文件作用是为了执行命令行调用，方便调试

from scrapy.cmdline import execute

import sys
import os


def doA():
    print('a')


def test():
    while True:
        print("bbbb")
        yield doA()


test().__next__()

# *通过scrapy crawl命令可以启动一个具体的爬虫

# 具体爬虫执行的命令需要在项目工程中运行，所以需要将项目工程添加到sys.path中
# 之后相当于在项目中执行scrapy命令
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 相当在命令行执行：scrapy crawl jobbole
execute(["scrapy", "crawl", "jobbole"])
