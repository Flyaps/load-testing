import argparse
import asyncio
import json
from datetime import datetime

from load_testing.core import collect_analytics, fetch_all, FetchRequest, Method


def headers(raw: str) -> dict:
    try:
        value = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise ValueError from exc
    if not isinstance(value, dict):
        raise ValueError
    return value


def parameters(raw: str) -> dict:
    return json.loads(raw)


def main():
    default_requests = 10
    default_timeout = 60

    parser = argparse.ArgumentParser('load_testing')
    parser.add_argument('-u', '--url', help='URL.', required=True, type=str)
    parser.add_argument('-m', '--method',
                        help=f'HTTP method, defaults to {Method.GET.value}',
                        choices=Method,
                        default=Method.GET.value,
                        type=Method)
    parser.add_argument('-head', '--headers',
                        help=('Headers in JSON format: '
                              """'{"Content-Type": "application/json"}'"""),
                        type=headers,
                        default='{}')
    parser.add_argument('-p', '--params',
                        help='Parameters. JSON string.',
                        type=parameters, default='{}')
    parser.add_argument('-n', '--amount',
                        help=f'Number of requests, defaults to {default_requests}.',
                        default=default_requests, type=int)
    parser.add_argument('-t', '--timeout',
                        help=f'Timeout to use, defaults to {default_timeout} seconds.',
                        default=default_timeout, type=float)
    args = parser.parse_args()

    request = FetchRequest(
        method=args.method.value,
        url=args.url,
        headers=args.headers,
        json=args.params,
    )
    amount = args.amount
    timeout = args.timeout

    print(f'Process started at {datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S%z")}')
    loop = asyncio.get_event_loop()
    fut = asyncio.gather(fetch_all(request, amount, timeout))
    results = loop.run_until_complete(fut)[0]
    collect_analytics(results)


if __name__ == '__main__':
    main()
