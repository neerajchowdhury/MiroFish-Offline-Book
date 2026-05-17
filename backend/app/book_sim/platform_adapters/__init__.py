"""Synthetic Swarmbook platform adapters."""

from .base import AdapterContext, BasePlatformAdapter
from .bookclub import BookclubAdapter
from .bookstagram import BookstagramAdapter
from .booktok import BookTokAdapter
from .goodreads import GoodreadsAdapter
from .newsletter import NewsletterAdapter
from .reddit import RedditAdapter
from .x_platform import XPlatformAdapter


PLATFORM_ADAPTERS = {
    "goodreads": GoodreadsAdapter,
    "kindle": GoodreadsAdapter,
    "booktok": BookTokAdapter,
    "reddit": RedditAdapter,
    "bookstagram": BookstagramAdapter,
    "x": XPlatformAdapter,
    "newsletter": NewsletterAdapter,
    "bookclub": BookclubAdapter,
}

__all__ = [
    "AdapterContext",
    "BasePlatformAdapter",
    "BookclubAdapter",
    "BookstagramAdapter",
    "BookTokAdapter",
    "GoodreadsAdapter",
    "NewsletterAdapter",
    "RedditAdapter",
    "XPlatformAdapter",
    "PLATFORM_ADAPTERS",
]
