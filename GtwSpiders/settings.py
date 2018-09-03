# -*- coding: utf-8 -*-

# Scrapy settings for GtwSpiders project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

import os


BOT_NAME = 'GtwSpiders'

SPIDER_MODULES = ['GtwSpiders.spiders']
NEWSPIDER_MODULE = 'GtwSpiders.spiders'


# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'GtwSpiders (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False  # 默认为True, 会读取网站上的robots协议，把不满足robots协议的URL过滤掉

# Configure maximum concurrent requests performed by Scrapy (default: 16)
#CONCURRENT_REQUESTS = 32

# Configure a delay for requests for the same website (default: 0)
# See https://doc.scrapy.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
#DOWNLOAD_DELAY = 3
# The download delay setting will honor only one of:
#CONCURRENT_REQUESTS_PER_DOMAIN = 16
#CONCURRENT_REQUESTS_PER_IP = 16

# Disable cookies (enabled by default)
#COOKIES_ENABLED = False

# Disable Telnet Console (enabled by default)
#TELNETCONSOLE_ENABLED = False

# Override the default request headers:
#DEFAULT_REQUEST_HEADERS = {
#   'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
#   'Accept-Language': 'en',
#}

# Enable or disable spider middlewares
# See https://doc.scrapy.org/en/latest/topics/spider-middleware.html
#SPIDER_MIDDLEWARES = {
#    'GtwSpiders.middlewares.GtwspidersSpiderMiddleware': 543,
#}

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
   # 'GtwSpiders.middlewares.GtwspidersDownloaderMiddleware': 543,
   'GtwSpiders.middlewares.RandomUserAgentMiddleware':555,
   # 'GtwSpiders.middlewares.RandomProxyMiddleware':556,
   'GtwSpiders.middlewares.JSPageMiddleware':1,
}
# 动态user-agent类型
# 可以自己修改为ie, chrome, firefox, safari, msie, opera等参数
# 具体值可以查看 https://github.com/hellysmile/fake-useragent
RANDOM_UA_TYPE = 'random'

# Enable or disable extensions
# See https://doc.scrapy.org/en/latest/topics/extensions.html
#EXTENSIONS = {
#    'scrapy.extensions.telnet.TelnetConsole': None,
#}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
# ITEM_PIPELINES是一个数据管道的登记表，每一项具体的数字代表它的优先级，数字越小，越早进入。
ITEM_PIPELINES = {
   'GtwSpiders.pipelines.GtwspidersPipeline': 300,
   # 'scrapy.pipelines.images.ImagesPipeline': 1,
   # 'GtwSpiders.pipelines.ArticleImagePipeline': 1,
   # 'GtwSpiders.pipelines.JsonWithEncodingPipeline': 2,
   # 'GtwSpiders.pipelines.JsonExporterPipeline': 2,
   # 'GtwSpiders.pipelines.MysqlPipeline': 3,
   # 'GtwSpiders.pipelines.MysqlTwistedPipeline': 3,
   'GtwSpiders.pipelines.ElasticSearchPipeline': 3,
}

# 图片地址从Item中获取时对应的属性值
IMAGES_URLS_FIELD = "front_image_url"
# 图片管道对图片获取后的存储地址
IMAGES_STORE = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'images')  # 放在settings.py同级的images目录下

# 关于图片管道图片大小过滤的配置
# IMAGES_MIN_HEIGHT = 100 # 图片为大于 100 x 100 的
# IMAGES_MIN_WIDTH = 100


# Enable and configure the AutoThrottle extension (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/autothrottle.html
#AUTOTHROTTLE_ENABLED = True
# The initial download delay
#AUTOTHROTTLE_START_DELAY = 5
# The maximum download delay to be set in case of high latencies
#AUTOTHROTTLE_MAX_DELAY = 60
# The average number of requests Scrapy should be sending in parallel to
# each remote server
#AUTOTHROTTLE_TARGET_CONCURRENCY = 1.0
# Enable showing throttling stats for every response received:
#AUTOTHROTTLE_DEBUG = False

# Enable and configure HTTP caching (disabled by default)
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html#httpcache-middleware-settings
#HTTPCACHE_ENABLED = True
#HTTPCACHE_EXPIRATION_SECS = 0
#HTTPCACHE_DIR = 'httpcache'
#HTTPCACHE_IGNORE_HTTP_CODES = []
#HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'

# mysql连接配置
MYSQL_HOST = "127.0.0.1"
MYSQL_DBNAME = "scrapy-spider"
MYSQL_USER = "root"
MYSQL_PASSWORD = "root"

# 日期格式化形式
SQL_DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"
SQL_DATE_FORMAT = "%Y-%m-%d"