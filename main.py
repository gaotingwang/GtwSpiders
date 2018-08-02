# -*- coding: utf-8 -*-

from scrapy.cmdline import execute

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 通过scrapy crawl命令可以启动一个具体的爬虫
# 相当在命令行执行：scrapy crawl jobbole
execute(["scrapy", "crawl", "jobbole"])
