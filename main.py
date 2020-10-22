import argparse
import json
import asyncio
from datetime import datetime
from collections import namedtuple

from load_test import Method, fetch_all, collect_analytics


def main():
    default_requests = 10
    default_timeout = 60

    parser = argparse.ArgumentParser()
    parser.add_argument('-m', '--method', help=f'HTTP method. {Method.available()}',
                        required=True, type=str)
    parser.add_argument('-u', '--url', help='URL.', required=True, type=str)
    parser.add_argument('-head', '--headers', help='Headers.', required=True, type=str)
    parser.add_argument('-p', '--params', help='Parameters.', required=False, type=str, default='{}')
    parser.add_argument('-n', '--amount',
                        help=f'Number of requests, defaults to {default_requests}.',
                        default=default_requests, type=int)
    parser.add_argument('-t', '--timeout',
                        help=f'Timeout to use, defaults to {default_timeout} seconds.',
                        default=default_timeout, type=float)
    args = parser.parse_args()

    Request = namedtuple('Request', ['method', 'url', 'headers', 'json'])
    request = Request(
        method=args.method,
        url=args.url,
        headers=json.loads(args.headers),
        json=json.loads(args.params)
    )
    amount = args.amount
    timeout = args.timeout

    Method.validate(request)

    print(f'Process started at {datetime.strftime(datetime.now(), "%Y-%m-%d %H:%M:%S%z")}')
    loop = asyncio.get_event_loop()
    results = loop.run_until_complete(asyncio.gather(fetch_all(request, amount, timeout)))[0]
    print(f'Successfully finished {results[results["status"] < 400].shape[0]} out of {amount} requests.')
    collect_analytics(results)


if __name__ == '__main__':
    main()
