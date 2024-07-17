from gevent import monkey
monkey.patch_all()
from gevent.pool import Pool
from queue import Queue
import schedule
import time

from core.db.mongo_pool import MongoPool
from core.proxy_validate.httpbin_validator import check_proxy
from settings import MAX_SCORE, TEST_PROXIES_ASYNC_COUNT, TEST_PROXIES_INTERVAL

class ProxyTester(object):
    """A class that performs the following operations:
    
    1. Retrieve all proxy IPs from the database.
    2. Validate each proxy IP's availability.
    3. If a proxy is unavailable, decrement its score. If its score reaches 0, delete it from the database; 
        otherwise, update the proxy IP in the database.
    4. If a proxy is available, restore its score to the maximum value and update the database.
    5. Perform these operations asynchronously to improve efficiency.
    6. Schedule these tasks to run at regular intervals.

    Attributes:
        mongo_pool (MongoPool): Instance for interacting with the database.
        queue (Queue): Queue for managing proxy IPs to be checked.
        coroutine_pool (Pool): Pool for managing asynchronous tasks.

    Methods:
        run(): Processes the core logic for testing proxy IPs.
        __check_one_proxy(): Checks the availability of a single proxy IP.
        __check_callback(temp): Callback function for asynchronous tasks.
        start(): Starts the proxy tester and schedules periodic checks.
    """
    def __init__(self):
        self.mongo_pool = MongoPool()
        self.queue = Queue()
        self.coroutine_pool = Pool()

    def __check_callback(self, temp):
        self.coroutine_pool.apply_async(self.__check_one_proxy, callback=self.__check_callback)

    def run(self):
        # put all proxy IPs into the queue
        proxies = self.mongo_pool.find_all()
        for proxy in proxies:
            self.queue.put(proxy)

        # initiate asynchronous tasks
        for i in range(TEST_PROXIES_ASYNC_COUNT):
            #  use loop to create multiple asynchronous tasks
            self.coroutine_pool.apply_async(self.__check_one_proxy, callback=self.__check_callback)

        # block the main thread until all tasks are completed
        self.queue.join()

    def __check_one_proxy(self):
        proxy = self.queue.get()

        proxy = check_proxy(proxy)

        # reduce score if proxy is unavailable
        if proxy.speed == -1:
            proxy.score -= 1

            # remove proxy if score reaches 0
            if proxy.score == 0:
                self.mongo_pool.delete(proxy)
            else:
                self.mongo_pool.update(proxy)
        # restore score if proxy is available
        else:
            proxy.score = MAX_SCORE
            self.mongo_pool.update(proxy)

        # signal that the task is complete
        self.queue.task_done()

    @classmethod
    def start(cls):
        proxy_tester = cls()
        proxy_tester.run()

        schedule.every(TEST_PROXIES_INTERVAL).hours.do(proxy_tester.run)
        while True:
            schedule.run_pending()
            time.sleep(1)

if __name__ == '__main__':
    pt = ProxyTester()
    pt.run()
    # ProxyTester.start()