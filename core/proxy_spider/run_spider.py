import importlib
import time
import schedule
from gevent import monkey
monkey.patch_all()
from gevent.pool import Pool

from settings import PROXIES_SPIDERS, SPIDER_INTERVAL
from utils.log import logger
from core.proxy_validate.httpbin_validator import check_proxy
from core.db.mongo_pool import MongoPool


class RunSpider(object):
    """Class to run proxy spiders, validate the proxies, and store valid proxies in the database.

    This class loads spiders based on configuration, fetches proxy IPs, validates them,
    and stores the valid ones in the database. It uses asynchronous execution to improve 
    efficiency and the `schedule` module to run the crawling tasks at regular intervals.

    Attributes:
        mongo_pool: an instance of the MongoPool class to interact with the MongoDB database.
        coroutine_pool: A gevent pool for managing coroutines.

    Methods:
        run(): main method to run all spiders asynchronously.
        _auto_import_instances(): dynamically import and instantiate spider classes based on configuration.
        __run_one_spider(spider): run a single spider to fetch and validate proxies, then stores them in the database.
        start(): class method to start the spider process and schedule it to run at regular intervals.
    """
    def __init__(self) -> None:
        self.mongo_pool = MongoPool()
        self.coroutine_pool = Pool()

    def run(self):
        spiders = self._auto_import_instances()

        for spider in spiders:
            self.coroutine_pool.apply_async(self.__run_one_spider, args=(spider,))
        
        # run all spiders asynchronously
        self.coroutine_pool.join()

    def _auto_import_instances(self):
        for full_class_name in PROXIES_SPIDERS:
            module_name, class_name = full_class_name.rsplit('.', maxsplit=1)
            module = importlib.import_module(module_name)
            cls = getattr(module, class_name)
            spider = cls()
            yield spider

    def __run_one_spider(self, spider):
        try:
            for proxy in spider.fetch_proxies():
                if proxy is None:
                    continue
                
                proxy = check_proxy(proxy)

                if proxy.speed != -1:
                    self.mongo_pool.insert(proxy)
        except Exception as ex:
            logger.exception(ex)
            logger.exception("Failed to crawl from {}".format(spider))

    @classmethod
    def start(cls):
        rs = RunSpider()
        rs.run()

        # schedule to run the spider at regular intervals
        schedule.every(SPIDER_INTERVAL).seconds.do(rs.run)
        while True:
            schedule.run_pending()
            time.sleep(1)


if __name__ == '__main__':
    rs = RunSpider()
    rs.run()