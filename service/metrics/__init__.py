from contextlib import contextmanager
import time as pytime

from .. import (
    settings,
    utils,
)

_instance = utils.import_string(settings.DEFAULT_METRICS_HANDLER)


def start(*args, **kwargs):
    """Handle any configuration required for metrics"""
    if settings.METRICS_ENABLED:
        _instance.start(*args, **kwargs)


def gauge(metric_name, value, *args, **kwargs):
    """Record the instantaneous value of a metric.

    The most recent value in a given flush interval will be recorded.

    """
    if settings.METRICS_ENABLED:
        _instance.gauge(metric_name, value, *args, **kwargs)


def increment(metric_name, value=1, *args, **kwargs):
    """Increment the counter by the given value"""
    if settings.METRICS_ENABLED:
        _instance.increment(metric_name, value, *args, **kwargs)


def histogram(metric_name, value, *args, **kwargs):
    """Sample a histogram value.

    Histograms will produce metrics that describe the distribution of the
    recorded values, namely the minimum, maximum, average, count and the
    75th, 85th, 95th and 99th percentiles.

    """
    if settings.METRICS_ENABLED:
        _instance.histogram(metric_name, value, *args, **kwargs)


@contextmanager
def time(metric_name, *args, **kwargs):
    """A decorator/contextmanager that will track the distribution of execution time"""
    start = pytime.time()
    try:
        yield
    finally:
        histogram(metric_name, pytime.time() - start, *args, **kwargs)


@contextmanager
def count(metric_name, *args, **kwargs):
    """A decorator/contextmanager that will increment a given metric each time"""
    increment(metric_name, *args, **kwargs)
    yield
