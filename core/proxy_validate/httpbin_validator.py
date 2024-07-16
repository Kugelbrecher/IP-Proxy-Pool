import time
import requests
import json

from settings import TEST_TIMEOUT
from domain import Proxy
from utils.http import get_request_header
from utils.log import logger

def check_proxy(proxy):
    """Revise the specified proxy IP for response speed, anonymity level, and supported protocol types.

    Args:
        proxy: Proxy model object.

    Returns:
        Proxy: Checked proxy model object.
    """
    # 准备代理IP字典
    proxies = {
        'http': "http://{}:{}".format(proxy.ip, proxy.port),
        'https': "https://{}:{}".format(proxy.ip, proxy.port)
    }

    # 测试该代理IP
    http, http_nick_type, http_speed = __check_http_proxy(proxies)
    https, https_nick_type, https_speed = __check_http_proxy(proxies, False)

    # 代理IP支持的协议类型, http是0, https是1, https和http都支持是2
    if http and https:
        proxy.protocol = 2
        proxy.nick_type = http_nick_type # https_* also ok
        proxy.speed = http_speed
    elif http:
        proxy.protocol = 0
        proxy.nick_type = http_nick_type
        proxy.speed = http_speed
    elif https:
        proxy.protocol = 1
        proxy.nick_type = https_nick_type
        proxy.speed = https_speed
    else:
        proxy.protocol = -1
        proxy.nick_type = -1
        proxy.speed = -1

    return proxy


def __check_http_proxy(proxies, is_http=True):
    """Check the specified proxy IP for response speed, anonymity level, and protocol type.

    Args:
        proxies: dictionary containing the proxy IP and port, formatted for HTTP and HTTPS.
        is_http: whether to check HTTP (True) or HTTPS (False). Defaults to True.

    Returns:
        tuple: A tuple containing a boolean indicating success, anonymity level, and speed.
    """
    nick_type = -1
    speed = -1

    if is_http:
        test_url = "http://httpbin.org/get"
    else:
        test_url = "https://httpbin.org/get"

    try:
        start = time.time()

        response = requests.get(test_url, 
                                headers=get_request_header(), 
                                proxies=proxies, 
                                timeout=TEST_TIMEOUT)
        
        if response.ok:
            speed = round(time.time() - start, 2)

            content = json.loads(response.text)
            origin = content['origin']
            proxy_connection = content['headers'].get('Proxy-Connection', None)
            # 1. transparent if ',' in origin that separates two IP addresses
            if ',' in origin:
                nick_type = 2
            # 2. anonymous if 'Proxy-Connection' in headers
            elif proxy_connection:
                nick_type = 1
            # 3. elite if neither of the above
            else:
                nick_type = 0

            return True, nick_type, speed
        return False, nick_type, speed
    
    except Exception as e:
        return False, nick_type, speed

if __name__ == '__main__':
    proxy = Proxy('117.74.65.207', '8118')
    rs = check_proxy(proxy)
    print(proxy.protocol)
    print(rs)