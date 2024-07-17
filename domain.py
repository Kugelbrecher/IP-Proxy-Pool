from settings import MAX_SCORE

class Proxy(object):
    """A network proxy object.

    Attributes:
        ip: IP address of the proxy.
        port: port number of the proxy.
        protocol: protocol type of the proxy (http->0, https->1, http&https->2).
        nick_type: anonymity level of the proxy (elite->0, anonymous->1, transparent->2).
        speed: speed of the proxy, in seconds.
        area: geographical area of the proxy.
        score: score of the proxy for ranking purposes.
        disable_domains: a list of domains where the proxy is disabled.

    Methods:
        __str__(): Converts the proxy object to a string representation of its dictionary.
    """
    def __init__(self, ip, port, protocol=-1, nick_type=-1, speed=-1, 
                 area=None, score=MAX_SCORE, disable_domains=[]) -> None:
        self.ip = ip
        self.port = port
        self.protocol = protocol
        self.nick_type = nick_type
        self.speed = speed
        self.area = area
        self.score = score
        self.disable_domains = disable_domains

    def __str__(self) -> str:
        return str(self.__dict__)