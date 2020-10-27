from typing import List

import pytest

from load_testing.core import collect_analytics, FetchResult


@pytest.mark.parametrize(
    'results,output', [
        ([],
         "0 requests ():\n"),
        ([FetchResult(1, 0, 0, 0.2, 200)],
         '1 requests (200: 1):\n'
         'Successful (1 out of 1):\n'
         '\tMean: 0.20000s; Median: 0.20000s\n'
         ),
        ([FetchResult(1, 0, 0, 0.2, 200),
          FetchResult(2, 0, 0, 0.3, 200),
          FetchResult(3, 0, 0, 0.3, 200),
          FetchResult(4, 0, 0, 0.3, 200)],
         '4 requests (200: 4):\n'
         'Successful (4 out of 4):\n'
         '\tMean: 0.27500s; Median: 0.30000s; Std: 0.05000s\n'
         ),
        ([FetchResult(1, 0, 0, 0.2, 400),
          FetchResult(2, 0, 0, 0.3, 500),
          FetchResult(3, 0, 0, 0.3, 500),
          FetchResult(4, 0, 0, 0.3, 502)],
         '4 requests (400: 1, 500: 2, 502: 1):\n'
         'Failed (4 out of 4):\n'
         '\tMean: 0.27500s; Median: 0.30000s; Std: 0.05000s\n'
         ),
        ([FetchResult(1, 0, 0, 0.2, 200),
          FetchResult(2, 0, 0, 0.3, 302),
          FetchResult(3, 0, 0, 0.4, 400),
          FetchResult(4, 0, 0, 0.5, 500)],
         '4 requests (200: 1, 302: 1, 400: 1, 500: 1):\n'
         'Successful (2 out of 4):\n'
         '\tMean: 0.25000s; Median: 0.25000s; Std: 0.07071s\n'
         'Failed (2 out of 4):\n'
         '\tMean: 0.45000s; Median: 0.45000s; Std: 0.07071s\n'
         ),
    ]
)
def test_collect_analytics(results: List[FetchResult], output: str, capsys):
    collect_analytics(results)
    captured = capsys.readouterr()
    assert str(captured.out) == output
