from .base import BaseMetricsHandler


class LocalMetricsHandler(BaseMetricsHandler):

    def start(self, *args, **kwargs):
        self._metrics = {
            'gauge': {},
            'increment': {},
            'histogram': {},
        }
        super(LocalMetricsHandler, self).start(*args, **kwargs)

    def gauge(self, metric_name, value, *args, **kwargs):
        super(LocalMetricsHandler, self).gauge(metric_name, value, *args, **kwargs)
        self._metrics['gauge'][metric_name] = value

    def increment(self, metric_name, value=1, *args, **kwargs):
        super(LocalMetricsHandler, self).increment(metric_name, value, *args, **kwargs)
        if metric_name not in self._metrics['increment']:
            self._metrics['increment'][metric_name] = 0
        self._metrics['increment'][metric_name] += value

    def histogram(self, metric_name, value, *args, **kwargs):
        super(LocalMetricsHandler, self).histogram(metric_name, value, *args, **kwargs)
        self._metrics['histogram'][metric_name] = value

instance = LocalMetricsHandler()
