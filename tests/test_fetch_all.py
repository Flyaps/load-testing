from collections import deque

from load_testing.core import fetch_all, FetchRequest
from tests.utils import get_url


async def test_fetch_all_results(test_server, capsys):
    async with test_server as server:
        url = get_url(server, 'echo-get')
        request = FetchRequest(
            'GET', str(url),
            headers={},
            json={}
        )
        amount, timeout = 5, 60
        results = await fetch_all(request, amount, timeout)
        assert len(results) == amount
        assert all(r.status == 200 for r in results)

        captured = capsys.readouterr()
        assert captured.out.count('Started. Process ') == amount
        assert captured.out.count('Finished. Process ') == amount


async def test_fetch_all_with_timeout(test_server, capsys):
    async with test_server as server:
        url = get_url(server, 'predefined-sleep')
        request = FetchRequest(
            'GET', str(url),
            headers={},
            json={}
        )
        timeout = 0.1
        delays = deque([0, 0, 0, 2, 0])
        amount = len(delays)
        test_server.app['delays'] = delays
        results = await fetch_all(request, amount, timeout)
        assert len(results) == amount - 1
        assert all(r.status == 200 for r in results)

        captured = capsys.readouterr()
        assert captured.out.count('Started. Process ') == amount
        assert captured.out.count('Finished. Process ') == amount - 1
