import asyncio
import statistics
from collections import Counter, namedtuple
from datetime import datetime
from enum import Enum
from itertools import filterfalse
from operator import attrgetter, methodcaller
from typing import Iterable, List

import aiohttp

FetchRequest = namedtuple('Request', ['method', 'url', 'headers', 'json'])
FetchResult = namedtuple('FetchResult', 'pid start finish delta status')


class Method(Enum):
    GET = 'GET'
    OPTIONS = 'OPTIONS'
    HEAD = 'HEAD'
    POST = 'POST'
    PUT = 'PUT'
    PATCH = 'PATCH'
    DELETE = 'DELETE'

    @classmethod
    def available(cls):
        return f'Available: {", ".join(cls.__members__.keys())}.'

    @classmethod
    def validate(cls, request):
        message = f'Method {request.method} is not supported. {cls.available()}'
        assert request.method in cls.__members__.keys(), message


def _collect_on_subset(subset: Iterable[FetchResult], total: int, status='Successful'):
    deltas = list(map(attrgetter('delta'), subset))
    if deltas:
        response = f'{status} ({len(deltas)} out of {total}):\n\t'
        stat_msg = [
            f'Mean: {statistics.mean(deltas):.5f}s',
            f'Median: {statistics.median(deltas):.5f}s'
        ]
        if len(deltas) > 1:
            dev = statistics.stdev(deltas)
            stat_msg.append(f'Std: {dev :.5f}s')
        print(response + '; '.join(stat_msg))


def collect_analytics(results: List[FetchResult]):
    counter = Counter(map(attrgetter('status'), results))
    count = ', '.join(
        f'{key}: {value}'
        for key, value in counter.items()
    )
    print(f'{len(results)} requests ({count}):')

    total_count = sum(counter.values())

    def is_successful(response):
        return response.status < 400

    successful = filter(is_successful, results)
    _collect_on_subset(successful, total_count)

    failed = filterfalse(is_successful, results)
    _collect_on_subset(failed, total_count, status='Failed')


async def fetch(session: aiohttp.ClientSession,
                request: FetchRequest,
                pid: int,
                timeout: aiohttp.ClientTimeout) -> FetchResult:
    start = datetime.now()
    print(f'Started. Process {pid} at {start}: sent to {request.url}')
    kwargs = {
        key: value
        for key, value in (('url', request.url), ('json', request.json))  # params))
        if value
    }
    async with session.request(request.method, timeout=timeout, **kwargs) as resp:
        status, finish = resp.status, datetime.now()
        delta = (finish - start).total_seconds()
        message = f'Process {pid} with code {resp.status}: {finish}, took: {delta:.2f} seconds'
        print(f'{"Finished" if status < 400 else "Failed"}. {message}')

        result = FetchResult(
            pid, start, finish, delta, status
        )
        return result


async def fetch_all(request: FetchRequest,
                    amount: int,
                    timeout: float) -> List[FetchResult]:
    client_timeout = aiohttp.ClientTimeout(total=timeout)
    async with aiohttp.ClientSession(headers=request.headers, timeout=client_timeout) as session:
        futures = [
            asyncio.ensure_future(fetch(session, request, i, client_timeout))
            for i in range(1, amount + 1)
        ]
        done, pending = await asyncio.wait(
            futures, timeout=timeout)

        for future in pending:
            future.cancel()

        results = list((map(methodcaller('result'), done)))
        results.sort(key=attrgetter('pid'))
        return results
