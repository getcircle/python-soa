import logging

from .base import BaseMetricsHandler


class LogMetricsHandler(BaseMetricsHandler):

    def __init__(self, *args, **kwargs):
        super(LogMetricsHandler, self).__init__(*args, **kwargs)
        self._log_level = logging.INFO

    def _get_logger(self, name=None, level=None):
        if not hasattr(self, '_logger'):
            if level is not None:
                self._log_level = level
            if name is None:
                name = 'metrics'
            self._logger = logging.getLogger(name)
        return self._logger

    def start(self, *args, **kwargs):
        self._get_logger(name=kwargs.get('name'), level=kwargs.get('level'))
        super(LogMetricsHandler, self).start(*args, **kwargs)

    def gauge(self, metric_name, value, *args, **kwargs):
        super(LogMetricsHandler, self).gauge(metric_name, value, *args, **kwargs)
        logger = self._get_logger()
        logger.log(self._log_level, 'gauge.%s:%s', metric_name, value)

    def increment(self, metric_name, value=1, *args, **kwargs):
        super(LogMetricsHandler, self).increment(metric_name, value, *args, **kwargs)
        logger = self._get_logger()
        logger.log(self._log_level, 'increment.%s:%s', metric_name, value)

    def histogram(self, metric_name, value, *args, **kwargs):
        super(LogMetricsHandler, self).histogram(metric_name, value, *args, **kwargs)
        logger = self._get_logger()
        logger.log(self._log_level, 'histogram.%s:%s', metric_name, value)

instance = LogMetricsHandler()
