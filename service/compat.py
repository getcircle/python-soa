"""
The `compat` module provides compatibility wrappers around optional packages.
"""

try:
    from datadog import (  # NOQA
        initialize,
        DogStatsd,
    )
except ImportError:
    initialize = None
    DogStatsD = None
