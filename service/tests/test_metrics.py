import time

from . import base
from .. import (
    control,
    metrics,
    settings,
)
from ..metrics import (
    base as base_metrics,
    local as local_metrics,
)


class TestMetrics(base.TestCase):

    def setUp(self):
        super(TestMetrics, self).setUp()
        control.set_metrics_handler(local_metrics.instance)
        metrics.start()

    def tearDown(self):
        super(TestMetrics, self).tearDown()
        control.set_metrics_handler(base_metrics.instance)

    def _verify_metric(self, metric_type, metric_name, value):
        self.assertEqual(self._get_metric(metric_type, metric_name), value)

    def _get_metric(self, metric_type, metric_name):
        return metrics.local.instance._metrics[metric_type][metric_name]

    def test_metrics_increment(self):
        metrics.increment('test')
        self._verify_metric('increment', 'test', 1)
        metrics.increment('test')
        self._verify_metric('increment', 'test', 2)
        metrics.increment('test', 2)
        self._verify_metric('increment', 'test', 4)

    def test_metrics_gauge(self):
        metrics.gauge('test', 3)
        metrics.gauge('test', 1)
        self._verify_metric('gauge', 'test', 1)

    def test_metrics_count(self):
        with metrics.count('test'):
            pass

        self._verify_metric('increment', 'test', 1)

    def test_metrics_time(self):
        with metrics.time('test'):
            time.sleep(0.001)

        value = self._get_metric('histogram', 'test')
        self.assertTrue(value >= 1 and value <= 2)

        with metrics.time('test2', use_ms=False):
            time.sleep(0.001)

        value = self._get_metric('histogram', 'test2')
        self.assertTrue(value >= 0.001 and value <= 0.002)

    def test_metrics_timing(self):
        metrics.timing('test', 0.001)
        value = self._get_metric('histogram', 'test')
        self.assertTrue(value >= 1 and value <= 2)

        metrics.timing('test2', 0.001, use_ms=False)
        value = self._get_metric('histogram', 'test2')
        self.assertTrue(value >= 0.001 and value <= 0.002)

    def test_metrics_histogram(self):
        metrics.histogram('test', 1)
        self._verify_metric('histogram', 'test', 1)

    def test_disable_metrics(self):
        original = settings.METRICS_ENABLED
        try:
            settings.METRICS_ENABLED = False
            metrics.increment('test')
            with self.assertRaises(KeyError):
                self._get_metric('increment', 'test')
        finally:
            settings.METRICS_ENABLED = original
