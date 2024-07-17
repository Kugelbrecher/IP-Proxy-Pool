from multiprocessing import Process
from core.proxy_spider.run_spider import RunSpider
from core.proxy_test import ProxyTester
from core.proxy_api import ProxyApi

def run():
    process_list = []
    process_list.append(Process(target=RunSpider.start))
    process_list.append(Process(target=ProxyTester.start))
    process_list.append(Process(target=ProxyApi.start))

    for process in process_list:
        # terminate the child process when the parent process exits
        process.daemon = True
        process.start()

    # block the parent process until the child process exits
    for process in process_list:
        process.join()

if __name__ == '__main__':
    run()