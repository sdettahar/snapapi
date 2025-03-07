# -*- coding: utf-8 -*-
# SNAP-API Logger
# Author: S Deta Harvianto <sdetta@gmail.com>

from typing import Union, Dict, Any, Callable, Awaitable
from fastapi import Request
from ulid import monotonic as ulid
from datetime import datetime
from starlette.responses import Response as StarletteResponse

from snapapi.responses import SNAPResponse


class SNAPLog:
    """ 
    UNTESTED: Logger Request and Response

    Class ini di-instantiate di setiap endpoint yang butuh Logger.
    Attribute `backend` berupa Callable yang hanya menerima 1 positional 
    argument type Dict[str, Any]
    """
    def __init__(
            self, 
            *, 
            namespace: Union[str, None] = None,
            service_code: Union[str, None] = None,  
            backend: Union[Callable[[Any], Dict[str, Any]], None] = None
        ) -> None:
        self.namespace = namespace
        self.service_code = service_code
        self.backend = backend

    async def send(
            self,
            *,
            request: Request,
            response: Union[SNAPResponse, StarletteResponse],
            exception: str = ''
        ) -> None:
        """ Build log if request and response are presented """

        # ULID is much better for Universal ID, as it shortable by timestamp
        uid = str(ulid.new())
        
        # Request
        remote_addr: str = ''
        if request.client:
            remote_addr = request.client.host
        user_agent: str = request.headers.get('user-agent', '')
        request_url: str = str(request.url)
        request_datetime: str = request.state.x_request_datetime
        request_headers: dict = dict(request.headers)
        request_body: Union[bytes, str] = await request.body()

        # Response
        status_code: int = response.status_code
        response_datetime: str = response.headers['x-timestamp']
        response_headers = dict(response.headers)
        response_body: Union[bytes, str] = response.body
        response_time: float = round((
                datetime.fromisoformat(response_datetime) \
                - datetime.fromisoformat(request_datetime)
            ).total_seconds(), 3)

        log = dict(
                uid=uid,
                namespace=self.namespace,
                service_code=self.service_code,
                response_time=response_time,
                status_code=status_code,
                remote_addr=remote_addr,
                user_agent=user_agent,
                request=dict(
                        request_url=request_url,
                        request_datetime=request_datetime,
                        request_headers=request_headers,
                        request_body=request_body
                    ),
                response=dict(
                        response_datetime = response_datetime,
                        response_headers=response_headers,
                        response_body=response_body
                    ),
                exception=exception
            )
        if self.backend:
            await self.backend(log)