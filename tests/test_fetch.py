import asyncio

import pytest
from aiohttp import ClientSession, ClientTimeout, web

from load_testing.core import fetch, FetchRequest
from tests.utils import get_url


async def test_fetch_get(test_server, capsys):
    async with test_server as server:
        url = get_url(server, 'echo-get')
        async with ClientSession() as session:
            request = FetchRequest('GET', str(url), {}, {})
            timeout = ClientTimeout(60)
            pid = 1
            result = await fetch(session, request, pid, timeout)
            assert result.status == web.HTTPOk.status_code
            assert result.pid == pid

            captured = capsys.readouterr()
            assert f'Finished. Process {pid} with code 200:' in captured.out


async def test_fetch_json(test_server, capsys):
    async with test_server as server:
        url = get_url(server, 'echo-json')
        async with ClientSession() as session:
            data = {'foo': 'bar'}
            request = FetchRequest(
                method='POST',
                url=str(url),
                headers={'Content-Type': 'application/json'},
                json=data
            )
            pid = 2
            timeout = ClientTimeout(60)
            assert 'json' not in server.app
            result = await fetch(session, request, pid, timeout)
            assert data == server.app['json']
            assert result.status == web.HTTPOk.status_code
            assert result.pid == pid

            captured = capsys.readouterr()
            assert f'Finished. Process {pid} with code 200:' in captured.out


async def test_fetch_bad_status(test_server, capsys):
    async with test_server as server:
        url = get_url(server, 'error_404')
        async with ClientSession() as session:
            request = FetchRequest(
                method='GET',
                url=str(url),
                headers={},
                json={}
            )
            pid = 5
            timeout = ClientTimeout(60)
            result = await fetch(session, request, pid, timeout)
            assert result.status == web.HTTPNotFound.status_code
            assert result.pid == pid

            captured = capsys.readouterr()
            assert f"Failed. Process {pid} with code 404:" in captured.out


async def test_fetch_timeout(test_server, capsys):
    async with test_server as server:
        delay = 400
        url = get_url(server, 'sleep').with_query(delay=delay)
        async with ClientSession() as session:
            request = FetchRequest(
                method='GET',
                url=str(url),
                headers={},
                json={}
            )
            pid = 3
            timeout = ClientTimeout(0.01)
            assert 'delay' not in server.app
            with pytest.raises(asyncio.TimeoutError):
                await fetch(session, request, pid, timeout)
            assert server.app['delay'] == delay
            # Don't show output in tests
            capsys.readouterr()
