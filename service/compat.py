"""
The `compat` module provides compatibility wrappers around optional packages.
"""

try:
    from dogapi import dog_stats_api
except ImportError:
    dog_stats_api = None
