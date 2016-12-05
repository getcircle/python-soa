

class BaseMetricsHandler(object):

    def start(self, *args, **kwargs):
        """Hook to allow any configuration required to start a metric handler"""
        pass

    def gauge(self, metric_name, value, *args, **kwargs):
        """Record the instantaneous value of a metric.

        The most recent value in a given flush interval will be recorded.

        """
        pass

    def increment(self, metric_name, value=1, *args, **kwargs):
        """Increment the counter by the given value"""
        pass

    def histogram(self, metric_name, value, *args, **kwargs):
        """Sample a histogram value.

        Histograms will produce metrics that describe the distribution of the
        recorded values, namely the minimum, maximum, average, count and the
        75th, 85th, 95th and 99th percentiles.

        """
        pass

instance = BaseMetricsHandler()
