# pylint: disable-all
# pylint comlains on astroid.exceptions.AttributeInferenceError: 'router' not found on <ClassDef.Application l.80 at 0x10b614fd0>.

import asyncio
import json
from collections import deque

import pytest
from aiohttp import web
from aiohttp.test_utils import TestServer


async def echo_get(request: web.Request) -> web.Response:
    msg = await request.text()
    return web.Response(text=msg)


async def echo_json(request: web.Request) -> web.Response:
    data = await request.json()
    request.app['json'] = data
    return web.Response(
        text=json.dumps(data),
        content_type='application/json'
    )


async def error_404(_) -> web.Response:
    raise web.HTTPNotFound()


async def get_sleep(request: web.Request) -> web.Response:
    delay = float(request.query.getone('delay', '300'))
    request.app['delay'] = delay
    await asyncio.sleep(delay)
    return web.Response()


async def get_predefined_sleep(request: web.Request) -> web.Response:
    delays: deque = request.app['delays']
    delay = delays.popleft()
    delays.append(delay)
    await asyncio.sleep(delay)
    return web.Response()


@pytest.fixture
def test_server(loop, aiohttp_unused_port) -> TestServer:
    app = web.Application()
    app.router.add_route('GET', '/get', echo_get, name='echo-get')
    app.router.add_route('POST', '/json', echo_json, name='echo-json')
    app.router.add_route('*', '/error/404', error_404, name='error_404')
    app.router.add_route('GET', '/get-sleep/', get_sleep, name='sleep')
    app.router.add_route('GET', '/predefined-sleep/',
                         get_predefined_sleep, name='predefined-sleep')
    server = TestServer(app, loop=loop, port=aiohttp_unused_port())
    return server
