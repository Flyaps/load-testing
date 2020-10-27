from aiohttp.test_utils import TestServer
from yarl import URL


def get_url(server: TestServer, name: str) -> URL:
    relative_url = server.app.router[name].url_for()
    url = server.make_url(str(relative_url))
    return url
