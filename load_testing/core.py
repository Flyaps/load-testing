from datetime import datetime
from collections import Counter
from enum import Enum

import asyncio
import aiohttp
import pandas as pd


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


def _collect_on_subset(subset, total, status='Successful'):
    if subset.shape[0]:
        response = f'{status} ({subset.shape[0]} out of {total}):\n\t'
        response += f'Mean: {subset["delta"].mean():.5f}s; '
        response += f'Median: {subset["delta"].median():.5f}s; '
        response += f'Std: {subset["delta"].std():.5f}s'
        print(response)


def collect_analytics(results):
    count = ', '.join(f'{key}: {value}'
                      for key, value in Counter(results['status']).items())
    print(f'{len(results)} requests ({count}):')

    successful = results[results['status'] < 400]
    _collect_on_subset(successful, results.shape[0])

    failed = results[results['status'] >= 400]
    _collect_on_subset(failed, results.shape[0], status='Failed')


async def fetch(session, request, pid, timeout: aiohttp.ClientTimeout):
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
        result = pd.DataFrame(
            [[pid, start, finish, delta, status]],
            columns=['pid', 'start', 'finish', 'delta', 'status']
        )
        return result


async def fetch_all(request, amount, timeout):
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

        results = pd.concat(map(lambda x: x.result(), done))
        results = results.sort_values(by=['pid']).set_index('pid')
        return results
