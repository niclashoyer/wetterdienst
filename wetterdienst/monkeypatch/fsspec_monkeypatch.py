# """Wetterdienst - Open weather data for humans"""
# -*- coding: utf-8 -*-
# Copyright (C) 2018-2021, earthobservations developers.
# Distributed under the MIT License. See LICENSE for more info.
"""
FSSPEC MONKEY PATCH

Code taken from
- FSSPEC (https://github.com/fsspec/filesystem_spec)
and
- our PR at (https://github.com/fsspec/filesystem_spec/pull/895)

For FSSPEC related code the license of the project (https://github.com/fsspec/filesystem_spec/blob/master/LICENSE)
.applies

TODO: remove this as soon as our PR is merged
"""
import logging
import warnings
from collections.abc import MutableMapping
from copy import copy
from pathlib import Path

import aiohttp
from fsspec import asyn
from fsspec.asyn import sync
from fsspec.dircache import DirCache
from fsspec.implementations import http

logger = logging.getLogger(__name__)


async def get_client(**kwargs):
    return aiohttp.ClientSession(**kwargs)


MemDirCache = DirCache


class HTTPFileSystem(http.HTTPFileSystem):
    def __init__(
        self,
        simple_links=True,
        block_size=None,
        same_scheme=True,
        size_policy=None,
        cache_type="bytes",
        cache_options=None,
        asynchronous=False,
        loop=None,
        client_kwargs=None,
        get_client=get_client,
        **storage_options,
    ):
        """
        NB: if this is called async, you must await set_client

        Parameters
        ----------
        block_size: int
            Blocks to read bytes; if 0, will default to raw requests file-like
            objects instead of HTTPFile instances
        simple_links: bool
            If True, will consider both HTML <a> tags and anything that looks
            like a URL; if False, will consider only the former.
        same_scheme: True
            When doing ls/glob, if this is True, only consider paths that have
            http/https matching the input URLs.
        size_policy: this argument is deprecated
        client_kwargs: dict
            Passed to aiohttp.ClientSession, see
            https://docs.aiohttp.org/en/stable/client_reference.html
            For example, ``{'auth': aiohttp.BasicAuth('user', 'pass')}``
        get_client: Callable[..., aiohttp.ClientSession]
            A callable which takes keyword arguments and constructs
            an aiohttp.ClientSession. It's state will be managed by
            the HTTPFileSystem class.
        storage_options: key-value
            Any other parameters passed on to requests
        cache_type, cache_options: defaults used in open
        """
        super().__init__(
            simple_links=simple_links,
            block_size=block_size,
            same_scheme=same_scheme,
            size_policy=size_policy,
            cache_type=cache_type,
            cache_options=cache_options,
            asynchronous=asynchronous,
            loop=loop,
            client_kwargs=client_kwargs,
            get_client=get_client,
            **storage_options,
        )
        request_options = copy(storage_options)
        self.use_listings_cache = request_options.pop("use_listings_cache", False)
        request_options.pop("listings_expiry_time", None)
        request_options.pop("max_paths", None)
        request_options.pop("skip_instance_cache", None)
        listings_cache_type = request_options.pop("listings_cache_type", None)
        listings_cache_location = request_options.pop("listings_cache_location", None)

        if self.use_listings_cache:
            if listings_cache_type == "filedircache":
                logger.info(f"Dircache located at {listings_cache_location}")

        self.kwargs = request_options

        if not asynchronous:
            sync(self.loop, self.set_session)


class FileDirCache(MutableMapping):
    def __init__(
        self,
        use_listings_cache=True,
        listings_expiry_time=None,
        listings_cache_location=None,
        **kwargs,
    ):
        """

        Parameters
        ----------
        use_listings_cache: bool
            If False, this cache never returns items, but always reports KeyError,
            and setting items has no effect
        listings_expiry_time: int or float (optional)
            Time in seconds that a listing is considered valid. If None,
            listings do not expire.
        listings_cache_location: str (optional)
            Directory path at which the listings cache file is stored. If None,
            an autogenerated path at the user folder is created.

        """
        import platformdirs
        from diskcache import Cache

        listings_expiry_time = listings_expiry_time and float(listings_expiry_time)

        if listings_cache_location:
            listings_cache_location = Path(listings_cache_location) / str(listings_expiry_time)
            listings_cache_location.mkdir(exist_ok=True, parents=True)
        else:
            listings_cache_location = Path(platformdirs.user_cache_dir(appname="wetterdienst-fsspec")) / str(
                listings_expiry_time
            )

        try:
            logger.info(f"Creating dircache folder at {listings_cache_location}")
            listings_cache_location.mkdir(exist_ok=True, parents=True)
        except Exception:
            logger.error(f"Failed creating dircache folder at {listings_cache_location}")

        self.cache_location = listings_cache_location

        self._cache = Cache(directory=listings_cache_location)
        self.use_listings_cache = use_listings_cache
        self.listings_expiry_time = listings_expiry_time

    def __getitem__(self, item):
        """Draw item as fileobject from cache, retry if timeout occurs"""
        return self._cache.get(key=item, read=True, retry=True)

    def clear(self):
        self._cache.clear()

    def __len__(self):
        return len(list(self._cache.iterkeys()))

    def __contains__(self, item):
        value = self._cache.get(item, retry=True)  # None, if expired
        if value:
            return True
        return False

    def __setitem__(self, key, value):
        if not self.use_listings_cache:
            return
        self._cache.set(key=key, value=value, expire=self.listings_expiry_time, retry=True)

    def __delitem__(self, key):
        del self._cache[key]

    def __iter__(self):
        return (k for k in self._cache.iterkeys() if k in self)

    def __reduce__(self):
        return (
            FileDirCache,
            (self.use_listings_cache, self.listings_expiry_time, self.cache_location),
        )


class AsyncFileSystem(asyn.AsyncFileSystem):
    def __init__(self, *args, **storage_options):
        """Create and configure file-system instance

        Instances may be cachable, so if similar enough arguments are seen
        a new instance is not required. The token attribute exists to allow
        implementations to cache instances if they wish.

        A reasonable default should be provided if there are no arguments.

        Subclasses should call this method.

        Parameters
        ----------
        use_listings_cache, listings_expiry_time, max_paths:
            passed to ``MemDirCache``, if the implementation supports
            directory listing caching. Pass use_listings_cache=False
            to disable such caching.
        skip_instance_cache: bool
            If this is a cachable implementation, pass True here to force
            creating a new instance even if a matching instance exists, and prevent
            storing this instance.
        asynchronous: bool
        loop: asyncio-compatible IOLoop or None
        """
        if self._cached:
            # reusing instance, don't change
            return
        self._cached = True
        self._intrans = False
        self._transaction = None
        self._invalidated_caches_in_transaction = []

        listings_cache_type = storage_options.get("listings_cache_type", "memdircache")
        if listings_cache_type not in ("memdircache", "filedircache"):
            raise ValueError("'listings_cache_type' has to be one of ('memdircache', 'filedircache')")
        if listings_cache_type == "memdircache":
            self.dircache = MemDirCache(**storage_options)
        else:
            self.dircache = FileDirCache(**storage_options)

        if storage_options.pop("add_docs", None):
            warnings.warn("add_docs is no longer supported.", FutureWarning, stacklevel=2)

        if storage_options.pop("add_aliases", None):
            warnings.warn("add_aliases has been removed.", FutureWarning, stacklevel=2)
        # This is set in _Cached
        self._fs_token_ = None


def activate():
    http.HTTPFileSystem = HTTPFileSystem
    asyn.AsyncFileSystem = AsyncFileSystem
