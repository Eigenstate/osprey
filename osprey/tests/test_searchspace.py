from __future__ import print_function, absolute_import, division

import sys
import numpy as np
import scipy.stats
from six.moves import xrange
from numpy.testing.decorators import skipif
try:
    from hyperopt import pyll
except ImportError:
    pass

from osprey.searchspace import SearchSpace


def test_1():
    s = SearchSpace()
    s.add_int('a', 1, 2)
    s.add_float('b', 2, 3)
    s.add_enum('c', ['a', 'b', 'c'])

    assert s.n_dims == 3

    assert s['a'].min == 1
    assert s['a'].max == 2
    assert s['a'].name == 'a'

    assert s['b'].min == 2
    assert s['b'].max == 3
    assert s['b'].name == 'b'

    assert s['c'].choices == ['a', 'b', 'c']
    assert s['c'].name == 'c'


def _run_chi2_test(values, bin_edges):
    n_samples = len(values)
    n_bins = len(bin_edges) - 1
    counts, bin_edges = np.histogram(values, bin_edges)
    p = scipy.stats.chisquare(counts, f_exp=[n_samples/n_bins] * n_bins)[1]
    if p < 0.001:
        raise ValueError('distribution not being sampled correctly, p=%f' % p)


def test_2_1():
    s = SearchSpace()
    s.add_int('a', 0, 3)

    values = [s.rvs()['a'] for _ in xrange(100)]
    _run_chi2_test(values, bin_edges=range(5))


@skipif('hyperopt.pyll' not in sys.modules, 'this test requires hyperopt')
def test_2_2():
    s = SearchSpace()
    s.add_int('a', 0, 3)
    values = [pyll.stochastic.sample(s['a'].to_hyperopt()) for _ in xrange(200)]
    _run_chi2_test(values, bin_edges=range(5))


def test_3_1():
    s = SearchSpace()
    s.add_float('b', -2, 2)

    values = [s.rvs()['b'] for _ in range(100)]
    assert all(-2 < v < 2 for v in values)
    _run_chi2_test(values, bin_edges=np.linspace(-2, 2, 10))


@skipif('hyperopt.pyll' not in sys.modules, 'this test requires hyperopt')
def test_3_2():
    s = SearchSpace()
    s.add_float('b', -2, 2)

    values = [pyll.stochastic.sample(s['b'].to_hyperopt()) for _ in xrange(100)]
    assert all(-2 < v < 2 for v in values)
    _run_chi2_test(values, bin_edges=np.linspace(-2, 2, 10))


def test_4_1():
    s = SearchSpace()
    s.add_enum('c', [True, False])

    values = [s.rvs()['c'] for _ in range(100)]
    assert all(v in [True, False] for v in values)
    _run_chi2_test(np.array(values, dtype=int), bin_edges=range(3))


@skipif('hyperopt.pyll' not in sys.modules, 'this test requires hyperopt')
def test_4_2():
    s = SearchSpace()
    s.add_enum('c', [True, False])

    values = [pyll.stochastic.sample(s['c'].to_hyperopt()) for _ in xrange(100)]
    assert all(v in [True, False] for v in values)
    _run_chi2_test(np.array(values, dtype=int), bin_edges=range(3))


def test_5_1():
    s = SearchSpace()
    s.add_float('a', 1e-5, 1, warp='log')

    n_bins = 10
    n_samples = 1000

    bin_edges = np.logspace(np.log10(s['a'].min), np.log10(s['a'].max),
                            num=n_bins+1)
    values = [s.rvs()['a'] for _ in xrange(n_samples)]

    _run_chi2_test(values, bin_edges)


@skipif('hyperopt.pyll' not in sys.modules, 'this test requires hyperopt')
def test_5_2():
    s = SearchSpace()
    s.add_float('a', 1e-5, 1, warp='log')

    bin_edges = np.logspace(np.log10(s['a'].min), np.log10(s['a'].max), num=5)
    values = [pyll.stochastic.sample(s['a'].to_hyperopt())
              for _ in xrange(100)]

    _run_chi2_test(values, bin_edges)
