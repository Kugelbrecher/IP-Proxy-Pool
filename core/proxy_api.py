from flask import Flask, request, jsonify
import json

from core.db.mongo_pool import MongoPool
from settings import PROXIES_MAX_COUNT

class ProxyApi(object):
    """A class to implement the Proxy Pool API module.

    This class provides high-availability proxy IP services for web crawlers. The API allows
    users to fetch random high-availability proxy IPs based on protocol type and domain, 
    fetch multiple high-availability proxy IPs, and append a disabled domain to a specified IP.

    Attributes:
        app (Flask): The Flask web service instance.
        mongo_pool (MongoPool): The MongoPool object for database operations.

    Methods:
        __init__(): Initializes the Flask web service and sets up the API routes.
        run(): Starts the Flask web service.
        start(): Class method to initialize and start the ProxyApi service.
    """
    def __init__(self):
        self.app = Flask(__name__ )
        self.mongo_pool = MongoPool()
 
        @self.app.route('/random')
        def random():
            try:
                protocol = request.args.get('protocol')
                domain = request.args.get('domain')
                proxy = self.mongo_pool.random_proxy(protocol, domain, count=PROXIES_MAX_COUNT)
                if proxy is None:
                    return jsonify({"error": "No proxies available"}), 404
                if protocol:
                    return '{}://{}:{}'.format(protocol, proxy.ip, proxy.port)
                else:
                    return '{}:{}'.format(proxy.ip, proxy.port)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
            
        @self.app.route('/proxies')
        def proxies():
            try:
                protocol = request.args.get('protocol')
                domain = request.args.get('domain')
                proxies = self.mongo_pool.get_proxies(protocol, domain, count=PROXIES_MAX_COUNT)
                proxies = [proxy.__dict__ for proxy in proxies]
                return json.dumps(proxies)
            except Exception as e:
                return jsonify({"error": str(e)}), 500

        @self.app.route('/disable_domain')
        def disable_domain():
            try:
                ip = request.args.get('ip')
                domain = request.args.get('domain')
                if not ip:
                    return 'Please provide IP parameter', 400
                if not domain:
                    return 'Please provide domain parameter', 400
                self.mongo_pool.disable_domain(ip, domain)
                return "Domain [{}] disabled for IP [{}]".format(domain, ip)
            except Exception as e:
                return jsonify({"error": str(e)}), 500
        
    def run(self):
        self.app.run('0.0.0.0', port=6860)

    @classmethod
    def start(cls):
        proxy_api = cls()
        proxy_api.run()

if __name__ == '__main__':
    ProxyApi.start()