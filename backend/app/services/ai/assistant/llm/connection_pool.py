import requests

class ConnectionPool:
    _instance = None

    @classmethod
    def get_session(cls) -> requests.Session:
        if cls._instance is None:
            cls._instance = requests.Session()
            # We can configure adapter settings if needed:
            # adapter = requests.adapters.HTTPAdapter(pool_connections=10, pool_maxsize=100)
            # cls._instance.mount('http://', adapter)
            # cls._instance.mount('https://', adapter)
        return cls._instance