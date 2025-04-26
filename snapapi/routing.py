# -*- coding: utf-8 -*-
# SNAP-API Routing
# Author: S Deta Harvianto <sdetta@gmail.com>

import logging
import sys
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.StreamHandler(sys.stdout))

from traceback import format_exc
from typing import Callable, Coroutine, Any, Optional, Union
from datetime import datetime, timezone, tzinfo

from fastapi.routing import APIRoute
from fastapi.exceptions import ValidationException
from starlette.requests import Request
from starlette.responses import Response as StarletteResponse

from snapapi import exceptions, codes
from snapapi.responses import SNAPResponse


class SNAPRoute(APIRoute):
    """ Routing Request/Response """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.namespace = None
        self.service_code = None
        self.logger = None

    def get_route_handler(self) -> Callable[
            [Request], 
            Coroutine[Any, Any, StarletteResponse]
        ]:
        """ Parse ValidationException yang sesuai OpenAPI ke SNAP """
        route_handler = super().get_route_handler()
        async def process_route(request: Request) -> StarletteResponse:
            # add x_request_datetime di request.state
            # DI SAAT Request diterima oleh API
            tz: Optional[tzinfo] = datetime.now().astimezone().tzinfo
            request_timestamp: str = datetime.now(tz)\
                                .isoformat(timespec="milliseconds")
            request.state.x_request_datetime = request_timestamp
            response: Optional[Union[SNAPResponse, StarletteResponse]]
            traceback: str = ''
            try:
                response = await route_handler(request)
            except Exception as exc:
                if isinstance(exc, ValidationException):
                    error = await exceptions.parse_validation_exception(exc)
                    message = error.message
                    additional_message = error.additional_message
                    status_code = error.status_code
                    case_code = error.case_code
                else:
                    if isinstance(exc, exceptions.SNAPException):
                        message = exc.message
                        additional_message = exc.additional_message
                        status_code = exc.status_code
                        case_code = exc.case_code
                    else:
                        error = exceptions.InternalServerError()
                        message = error.message
                        additional_message = error.additional_message
                        status_code = error.status_code
                        case_code = error.case_code

                # cuma status_code 5xx yg dilog
                if status_code >=500:
                    traceback = format_exc()
                    _logger.error(exc, exc_info=True)

                responseCode = f'{status_code}{self.service_code}{case_code}'
                responseMessage = message
                if additional_message:
                    responseMessage += ' ' 
                    responseMessage += additional_message
                
                response = SNAPResponse(
                    status_code=status_code,
                    content=dict(
                            responseCode=responseCode,
                            responseMessage=responseMessage
                        ))

            # Add default timestamp, cache-control
            response_timestamp: str = datetime.now(tz).isoformat(
                                        timespec="milliseconds")
            response.headers.update({
                    'x-timestamp': response_timestamp,
                    'cache-control': 'no-store'
                })
            # Logger
            if self.logger:
                await self.logger.send(
                        request=request,
                        response=response,
                        traceback=traceback
                    )
            return response
        return process_route