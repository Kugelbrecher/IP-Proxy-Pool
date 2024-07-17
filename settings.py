import logging

# score of proxy ip
MAX_SCORE = 50

# log settings
LOG_LEVEL = logging.DEBUG
LOG_FMT = '%(asctime)s %(filename)s [line:%(lineno)d] %(levelname)s: %(message)s'
LOG_DATEFMT = '%Y-%m-%d %H:%M:%S'
LOG_FILENAME = 'log.log'

# MongoDB
# if cloud atlas:
# MONGO_URL = "mongodb+srv://<username>:<password>@cluster0.bm07zwz.mongodb.net/?retryWrites=true&w=majority"
# if local:
MONGO_URL = "mongodb://127.0.0.1:27017"

# spider class name/path: module.class
PROXIES_SPIDERS = [
    'core.proxy_spider.proxy_spiders.Ip3366Spider',
    'core.proxy_spider.proxy_spiders.KuaiSpider',
    'core.proxy_spider.proxy_spiders.ProxylistplusSpider',
]

SPIDER_INTERVAL = 10

# test proxy
TEST_TIMEOUT = 10

# number of asynchronous proxy IP detection
TEST_PROXIES_ASYNC_COUNT = 10
# time interval for checking the proxy IP, in hours
TEST_PROXIES_INTERVAL = 2

# maximum number of proxy IPs obtained; 
# the smaller this number, the higher the availability; but the randomness is worse
PROXIES_MAX_COUNT = 0