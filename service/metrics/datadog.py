from ..compat import dog_stats_api
from ..exceptions import ImproperlyConfigured
from .base import BaseMetricsHandler


class DataDogMetricsHandler(BaseMetricsHandler):

    def start(self, *args, **kwargs):
        if 'api_key' not in kwargs:
            raise ImproperlyConfigured(
                '"api_key" must be provided to start data dog metrics handler"'
            )

        dog_stats_api.start(api_key=kwargs['api_key'])
        super(DataDogMetricsHandler, self).start(*args, **kwargs)

    def gauge(self, *args, **kwargs):
        super(DataDogMetricsHandler, self).gauge(*args, **kwargs)
        dog_stats_api.gauge(*args, **kwargs)

    def increment(self, *args, **kwargs):
        super(DataDogMetricsHandler, self).increment(*args, **kwargs)
        dog_stats_api.increment(*args, **kwargs)

    def histogram(self, *args, **kwargs):
        super(DataDogMetricsHandler, self).histogram(*args, **kwargs)
        dog_stats_api.histogram(*args, **kwargs)

instance = DataDogMetricsHandler()
