from ..compat import (
    initialize,
    DogStatsd,
)
from ..exceptions import ImproperlyConfigured
from .base import BaseMetricsHandler


class DataDogMetricsHandler(BaseMetricsHandler):

    def start(self, *args, **kwargs):
        if 'api_key' not in kwargs:
            raise ImproperlyConfigured(
                '"api_key" must be provided to start data dog metrics handler"'
            )
        elif 'app_key' not in kwargs:
            raise ImproperlyConfigured(
                '"app_key" must be provided to start data dog metrics handler"'
            )

        initialize(api_key=kwargs.pop('api_key'), app_key=kwargs.pop('app_key'))
        self._statsd = DogStatsd(**kwargs)
        super(DataDogMetricsHandler, self).start(*args, **kwargs)

    def gauge(self, *args, **kwargs):
        super(DataDogMetricsHandler, self).gauge(*args, **kwargs)
        self._statsd.gauge(*args, **kwargs)

    def increment(self, *args, **kwargs):
        super(DataDogMetricsHandler, self).increment(*args, **kwargs)
        self._statsd.increment(*args, **kwargs)

    def histogram(self, *args, **kwargs):
        super(DataDogMetricsHandler, self).histogram(*args, **kwargs)
        self._statsd.histogram(*args, **kwargs)

instance = DataDogMetricsHandler()
