import time
import random

from core.proxy_spider.base_spider import BaseSpider

class Ip3366Spider(BaseSpider):
    urls = ['http://www.ip3366.net/free/?stype=1&page={}'.format(i) for i in range(1, 10)]
    group_xpath = '//*[@id="list"]/table/tbody/tr'
    detail_xpath = {
        'ip':'./td[1]/text()', 
        'port':'./td[2]/text()', 
        'area':'./td[5]/text()'
        }

class KuaiSpider(BaseSpider):
    urls = ['https://www.kuaidaili.com/free/inha/{}/'.format(i) for i in range(1, 10)]
    group_xpath = '//*[@id="list"]/div[2]/table/tbody/tr'
    detail_xpath = {
        'ip':'./td[1]/text()', 
        'port':'./td[2]/text()', 
        'area':'./td[5]/text()'
        }

    def get_page_from_url(self, url):
        time.sleep(random.uniform(1, 3))
        return super().get_page_from_url(url) # call the parent class method

class ProxylistplusSpider(BaseSpider):
    urls = ['https://list.proxylistplus.com/Fresh-HTTP-Proxy-List-{}'.format(i) for i in range(1, 2)]
    group_xpath = '//*[@id="page"]/table[2]/tr[position()>2]'
    detail_xpath = {
        'ip':'./td[2]/text()',
        'port':'./td[3]/text()',
        'area':'./td[5]/text()'
    }


if __name__ == '__main__':
    spider = ProxylistplusSpider()

    for proxy in spider.fetch_proxies():
        print(proxy)
      