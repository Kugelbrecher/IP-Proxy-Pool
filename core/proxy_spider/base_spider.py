import requests
from lxml import etree

from utils.http import get_request_header
from domain import Proxy

class BaseSpider(object):
    """A generic web spider for extracting proxy IP addresses.

    This class is designed to scrape proxy IP information from various websites by 
    specifying different URL lists, group XPaths, and detail XPaths. It extracts 
    the IP address, port number, and area information of proxies from web pages.

    Attributes:
        urls: list of URLs to scrape proxy IPs from.
        group_xpath: XPath to group elements containing proxy information.
        detail_xpath: dictionary of XPaths for extracting proxy details 
                    with keys 'ip', 'port', and 'area'.

    Args:
        urls: list of URLs to scrape proxy IPs from. Defaults to an empty list.
        group_xpath: XPath to group elements containing proxy information. Defaults to an empty string.
        detail_xpath: dictionary of XPaths for extracting proxy details. Defaults to an empty dictionary.

    Methods:
        fetch_proxies(): Generator method to retrieve proxies as Proxy objects.
        get_page_from_url(url): Fetches the page content for a given URL.
        get_proxies_from_page(page): Parses the page content and extracts proxy details.
        get_first_from_list(lst): Returns the first element from a list or an empty string if the list is empty.
    """
    urls = []
    group_xpath = ''
    detail_xpath = {}

    def __init__(self, urls=[], group_xpath='', detail_xpath={}):
        if urls:
            self.urls = urls
        if group_xpath:
            self.group_xpath = group_xpath
        if detail_xpath:
            self.detail_xpath = detail_xpath

    def fetch_proxies(self):
        for url in self.urls:
            page = self.get_page_from_url(url)
            proxies = self.get_proxies_from_page(page)
            yield from proxies # proxies is a generator from yield, so yield + from
 
    def get_page_from_url(self, url):
        response = requests.get(url, headers=get_request_header())
        return response.content
    
    def get_proxies_from_page(self, page):
        element = etree.HTML(page)
        trs = element.xpath(self.group_xpath)
        for tr in trs:
            ip = self.get_first_from_list(tr.xpath(self.detail_xpath['ip']))
            port = self.get_first_from_list(tr.xpath(self.detail_xpath['port']))
            area = self.get_first_from_list(tr.xpath(self.detail_xpath['area']))
            proxy = Proxy(ip, port, area=area)
            yield proxy

    def get_first_from_list(self, lst):
        return lst[0].strip() if len(lst) != 0 else ''


if __name__ == '__main__':
    config = {
        'urls':['http://www.ip3366.net/free/?stype=1&page={}'.format(i) for i in range(1, 2)],
        'group_xpath': '//*[@id="list"]/table/tbody/tr',
        'detail_xpath': {
            'ip':'./td[1]/text()', 
            'port':'./td[2]/text()', 
            'area':'./td[5]/text()'
            },
    }
    base_spider = BaseSpider(**config)
    for proxy in base_spider.fetch_proxies():
        print(proxy)