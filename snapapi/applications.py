# -*- coding: utf-8 -*-
# SNAP-API Main
# Author: S Deta Harvianto <sdetta@gmail.com>

from typing import Type, TypeVar, Any, Union
from typing_extensions import Annotated, Doc

from starlette.responses import Response
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import FastAPI, Request
from fastapi.datastructures import Default

from snapapi.responses import SNAPResponse
from snapapi.cache import SNAPCache

AppType = TypeVar("AppType", bound="SNAPAPI")

class SNAPAPI(FastAPI):
    def __init__(
        self: AppType, 
        *, 
        namespace: Annotated[
            str,
            Doc(
                """
                **TODO**
                String yang digunakan sebagai Kode PJP.
                Misal:
                - Bank BRI, 'bri'
                - Bank Mandiri, 'mandiri'
                - Xendit, 'xendit'
                - dstnya

                Namespace ini akan banyak digunakan di hampir semua
                class dan method SNAP-API.
                """
            )
        ] = '',
        title: Annotated[
            str,
            Doc(
                """
                The title of the API.

                It will be added to the generated OpenAPI (e.g. visible at `/docs`).

                Read more in the
                [FastAPI docs for Metadata and Docs URLs](https://fastapi.tiangolo.com/tutorial/metadata/#metadata-for-api).

                **Example**

                ```python
                from fastapi import FastAPI

                app = FastAPI(title="ChimichangApp")
                ```
                """
            ),
        ] = "SNAP-API",
        description: Annotated[
            str,
            Doc(
                """
                Deskripsi mengenai aplikasi ini. Support Markdown
                dengan [CommonMark syntax](https://commonmark.org/)
                """
            )
        ] = "SNAP (Standar Nasional Open API Pembayaran) Versi 1.0.2",
        default_response_class: Annotated[
            Type[Response],
            Doc(
                """
                Default Response class menggunakan SNAPResponse
                """
            )
        ] = Default(SNAPResponse),
        **kwargs
    ) -> None:
        super().__init__(
                title=title,
                description=description, 
                default_response_class=default_response_class,
                **kwargs
            )
        self._namespace = namespace
        self._cache = self.set_cache()

    @property
    def namespace(self):
        return self._namespace

    @namespace.setter
    def namespace(self, namespace: str) -> None:
        self._namespace = namespace
        self.set_cache()

    def set_cache(self) -> Any:
        cache = SNAPCache(self._namespace).cache
        self._cache = cache
        return cache


async def http_exception_handler(
        cache: SNAPCache,
        request: Request,
        exc: StarletteHTTPException
    ) -> SNAPResponse:
    """ 
    TODO: LEARN {fastapi}/applications.py:947 biar nyambung

    Do:
    1.  Delete cache key X-External-ID, jika status_code >=500 sehingga 
        Transactional Request bisa diulang dengan X-External-ID yang sama
    2.  Error Response sesuai dengan standard SNAP
    """
    if cache and exc.status_code >=500:
        await cache.delete(
                headers=dict(request.headers),
                status_code=exc.status_code
            )
    return SNAPResponse(
            status_code=exc.status_code, 
            content=exc.detail,
            headers=exc.headers
        )