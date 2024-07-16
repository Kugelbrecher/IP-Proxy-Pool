import random
import pymongo
from pymongo import MongoClient

from settings import MONGO_URL
from domain import Proxy
from utils.log import logger

class MongoPool(object):
    """A class to manage proxy pool operations on a MongoDB collection.

    This class provides methods to interact with a MongoDB collection containing proxy data. 
    It includes basic CRUD operations and additional functionalities to support a proxy API.

    Attributes:
        client (MongoClient): The MongoDB client connection.
        proxies (Collection): The MongoDB collection for proxies.

    Methods:
        insert(proxy): Inserts a new proxy into the collection.
        update(proxy): Updates an existing proxy in the collection.
        delete(proxy): Deletes a proxy from the collection based on its IP.
        find_all(): Yields all proxies in the collection.
        find(conditions, count): Finds proxies based on given conditions and count limit.
        get_proxies(protocol, domain, count, nick_type): Retrieves a list of proxies based on protocol, domain, and other parameters.
        random_proxy(protocol, domain, count, nick_type): Retrieves a random proxy based on protocol, domain, and other parameters.
        disable_domain(ip, domain): Adds a domain to the disable_domain list of a specified IP.
    """
    def __init__(self):
        self.client = MongoClient(MONGO_URL)
        self.proxies = self.client['proxies_pool']['proxies'] # auto create db and collection

    def close(self):
        self.client.close()

    def insert(self, proxy=None):
        if proxy:
            # check if proxy already exists
            count = self.proxies.count_documents({'_id': proxy.ip})
            if count != 0:
                logger.warning("Proxy already exists:{}".format(proxy))
                return

            # insert the proxy into the collection
            proxy_dic = proxy.__dict__ # convert Proxy object to dict
            proxy_dic['_id'] =  proxy.ip # define the primary key to be the IP address
            self.proxies.insert_one(proxy_dic)
            logger.info("Insert proxy:{}".format(proxy))
        else:
            logger.error("No proxy provided to insert")

    def update(self, proxy=None):
        if proxy:
            self.proxies.update_one({'_id': proxy.ip}, {'$set': proxy.__dict__})
            logger.info("Update proxy:{}".format(proxy))
        else:
            logger.error("No proxy provided to update")

    def delete(self, proxy=None):
        if proxy:
            self.proxies.delete_one({'_id': proxy.ip})
            logger.info("Delete proxy:{}".format(proxy))
        else:
            logger.warning("No proxy provided to delete")

    def find_all(self):
        cursor = self.proxies.find()
        for item in cursor:
            item.pop('_id')
            proxy = Proxy(**item)
            yield proxy

    def find(self, conditions={}, count=0):
        """Find proxies based on given conditions and count limit.

        Args:
            conditions: conditions to filter proxies.
            count: maximum number of proxies to retrieve. Default is 0 (no limit).

        Returns:
            list: A list of proxies that match the conditions, sorted by score and speed.
        """
        cursor = self.proxies.find(conditions, limit=count).sort([
            ('score', pymongo.DESCENDING),
            ('speed', pymongo.ASCENDING)
        ])

        proxy_list = []
        for item in cursor:
            item.pop('_id')
            proxy = Proxy(**item)
            proxy_list.append(proxy)

        return proxy_list
    
    def get_proxies(self, protocol=None, domain=None, count=0, nick_type=0):
        """API to retrieve a list of proxies based on protocol, domain, and other parameters.

        Args:
            protocol: protocol type of the proxy (http, https).
            domain: domain to be accessed.
            count: number of proxies to retrieve. Default is 0 (no limit).
            nick_type: anonymity level of the proxy (elite->0, anonymous->1, transparent->2).

        Returns:
            list: A list of proxies that match the criteria.
        """
        conditions = {'nick_type': nick_type}

        if protocol is None:
            conditions['protocol'] = 2
        elif protocol.lower() == 'http':
            conditions['protocol'] = {'$in': [0, 2]}
        else:
            conditions['protocol'] = {'$in': [1, 2]}

        if domain:
            conditions['disable_domains'] = {'$nin': [domain]}

        return self.find(conditions, count=count)
    
    def random_proxy(self, protocol=None, domain=None, count=0, nick_type=0):
        """API to retrieve a random proxy based on protocol, domain, and other parameters.

        Args:
            protocol: protocol type of the proxy (http, https).
            domain: domain to be accessed.
            count: number of proxies to retrieve. Default is 0 (no limit).
            nick_type: anonymity level of the proxy (elite->0, anonymous->1, transparent->2).

        Returns:
            Proxy: A random proxy that matches the criteria.
        """
        proxy_list = self.get_proxies(protocol=protocol, 
                                      domain=domain, 
                                      count=count, 
                                      nick_type=nick_type)
        return random.choice(proxy_list)
    
    def disable_domain(self, ip, domain):
        """Add a domain to the disable_domain list of a specified IP.

        Args:
            ip (str): The IP address.
            domain (str): The domain to be disabled.

        Returns:
            bool: True if the domain was successfully added, False otherwise.
        """
        if self.proxies.count_documents({'_id': ip, 'disable_domains':domain}) == 0:
            self.proxies.update_one({'_id': ip}, {'$push': {'disable_domains': domain}})
            return True
        return False

if __name__ == '__main__':
    mongo = MongoPool()
    try:
        proxy = Proxy('124.89.97.43', '80', protocol=1, nick_type=0, speed=0.36, area='China')
        mongo.insert(proxy)
        proxy = Proxy('124.89.97.43', '80', protocol=2, nick_type=0, speed=0.36, area='China')
        mongo.insert(proxy)
        proxy = Proxy('124.89.97.44', '80', protocol=1, nick_type=0, speed=0.36, area='China')
        mongo.insert(proxy)
        proxy = Proxy('124.89.97.45', '80', protocol=0, nick_type=0, speed=0.36, area='China')
        mongo.insert(proxy)
        proxy = Proxy('124.89.97.46', '80', protocol=0, nick_type=2, speed=0.36, area='China')
        mongo.insert(proxy)

        proxy = Proxy('124.89.97.46', '8118', protocol=0, nick_type=2, speed=0.36, area='China')
        mongo.update(proxy)

        proxy = Proxy('124.89.97.46', '8118')
        mongo.delete(proxy)

        for pr in mongo.find_all():
            print(pr)

        cond = {'nick_type': 1}
        for pr in mongo.find(cond):
            print(pr)

        for pr in mongo.get_proxies(protocol='http'):
            print(pr)
    finally:
        mongo.close()