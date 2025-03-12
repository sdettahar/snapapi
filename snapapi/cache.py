# -*- coding: utf-8 -*-
# SNAP-API Cache
# Author: S Deta Harvianto <sdetta@gmail.com>

import asyncio
import logging
import sys
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.StreamHandler(sys.stdout))

try:
    import aiocache
    HAS_AIOCACHE = True
except ModuleNotFoundError:
    HAS_AIOCACHE = False

from typing import Callable, TypeVar, Union, Literal, Any, Dict
from annotated_types import Len
from typing_extensions import Annotated

from snapapi.exceptions import TimeOut
from snapapi.codes import STATUS_CODE_409, STATUS_CODE_500, STATUS_CODE_504

AppType = TypeVar("AppType", bound="SNAPCache")


class SNAPCache:
    """
    Fitur SNAPCache hanya dua, `add` dan `delete`.

    - `add`:    setelah request selesai diverifikasi, add key X-External-Id
                ke Cache. By default TTL adalah sisa detik hingga jam 24:00
                pada hari ini. Secara otomatis backend ('memory', 'redis', 
                'memcached') akan menghapus keys saat TTL expires
    - `delete`  jika ada error status code >=500, sebaiknya X-External-Id 
                dihapus, sehingga bisa digunakan kembali tanpa harus 
                `Conflict`

    Note:   backend 'memory' hanya digunakan saat Dev, karena setiap kali 
            woker reload, keys pasti akan hilang.
            Di Production gunakan antara 'memcached' atau 'redis'
    """
    def __init__(
            self: AppType,
            namespace: str,
            /,
            host: Union[str, None] = None,
            port: Union[int, None] = None,
            db: Union[int, None] = None,
            timeout: Union[int, None] = 9,
            backend: Union[str, None] = None
        ) -> None:
        self._namespace = namespace
        self._host = host
        self._port = port
        self._db = db
        self._backend = backend
        self._timeout = timeout
        self._cache = self.initiate_cache()

    @property
    def namespace(self):
        return self._namespace
    
    @namespace.setter
    def namespace(self, namespace: str) -> None:
        self._namespace = namespace
        self.initiate_cache()

    @property
    def host(self) -> Union[str, None]:
        return self._host

    @host.setter
    def host(self, host: Union[str, None]) -> None:
        self._host = host
        self.initiate_cache()

    @property
    def port(self) -> Union[int, None]:
        return self._port

    @port.setter
    def port(self, port: Union[int, None]) -> None:
        self._port = port
        self.initiate_cache()
    
    @property
    def db(self) -> Union[int, None]:
        return self._db

    @db.setter
    def db(self, db: Union[int, None]) -> None:
        self._db = db
        self.initiate_cache()
    
    @property
    def timeout(self) -> Union[int, None]:
        return self._timeout

    @timeout.setter
    def timeout(self, timeout: Union[int, None]) -> None:
        self._timeout = timeout
        self.initiate_cache()
    
    @property
    def backend(self) -> Union[str, None]:
        return self._backend

    @backend.setter
    def backend(self, value: Union[str, None]) -> None:
        self._backend = value
        self.initiate_cache()

    @property
    def cache(self) -> Any:
        """ 
        Readonly. Hanya berubah jika attributes lain berubah
        """
        return self._cache
    
    def initiate_cache(self) -> Any:
        """ 
        NEXT: mungkin akan replace `aiocache` karena kebutuhan SNAP
        cukup simple
        """
        cache = None
        if not HAS_AIOCACHE or not self._namespace:
            self._cache = cache
        else:
            if self._backend == 'redis': # assume redis
                host = self._host or 'localhost'
                port = self._port or 6379
                db = self._db or 8
                cache = aiocache.Cache(
                        aiocache.Cache.REDIS,
                        namespace=self._namespace,
                        endpoint=host,
                        port=port,
                        db=db,
                        timeout=self._timeout
                    )
            elif self._backend == 'memcached':
                host = self._host or 'localhost'
                port = self._port or 11211
                cache = aiocache.Cache(
                        aiocache.Cache.MEMCACHED,
                        namespace=self._namespace,
                        endpoint=host,
                        port=port,
                        timeout=self._timeout
                    )
            else:
                cache = aiocache.Cache(
                        aiocache.Cache.MEMORY, 
                        namespace = self._namespace
                    )
                _logger.warning('Cache Memory hanya untuk Demo. '\
                    'Setiap kali worker/server restart, keys akan hilang')
            self._cache = cache
        return cache

    def __str__(self) -> str:
        return f'namespace: {self.namespace}, cache: {self.cache}'

    def __repr__(self)->str:
        return f"{self.__class__.__name__}({self.__str__()})"

    async def add(
            self,
            key: str,
            value: Union[Any, None] = None,
            ttl: Union[int, None] = None
        ) -> None:
        """ Cache Key and Value """
        if not self.cache:
            return None
        try:
            await self.cache.add(key=key, value=value, ttl=ttl)
        except asyncio.TimeoutError:
            raise TimeOut()
        finally:
            await self.cache.close()

    async def delete(self, key: str) -> None:
        """ Delete Key """
        if not self.cache:
            return None
        try:
            await self.cache.delete(key)
        except:
            pass
        finally:
            await self.cache.close()

    async def exists(self, key: str) -> bool:
        if not self.cache:
            return False
        try:
            res = await self.cache.exists(key)
            return res and True or False
        except asyncio.TimeoutError:
            raise TimeOut()
        finally:
            await self.cache.close()