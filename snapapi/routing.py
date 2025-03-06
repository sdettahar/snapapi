# -*- coding: utf-8 -*-
# SNAP-API Routing
# Author: S Deta Harvianto <sdetta@gmail.com>

import logging
import sys
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.StreamHandler(sys.stdout))

from collections import defaultdict
from typing import Callable, Coroutine, Any, Optional
from datetime import datetime, timezone, tzinfo

from fastapi.routing import APIRoute
from fastapi.exceptions import ValidationException
from starlette.requests import Request
from starlette.responses import Response

from snapapi import exceptions, codes, SNAPResponse


class SNAPRoute(APIRoute):
    """ Routing Request/Response """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.namespace = None
        self.service_code = None

    def get_route_handler(self)->Callable[
            [Request], Coroutine[Any, Any, Response]
        ]:
        """ Parse ValidationException yang sesuai OpenAPI ke SNAP """
        route_handler = super().get_route_handler()
        async def error_handler(request: Request) -> Response:
            # add x_request_datetime di request.state
            # DI SAAT Request diterima oleh API
            tz: Optional[tzinfo] = datetime.now().astimezone().tzinfo
            request_timestamp: str = datetime.now(tz)\
                                .isoformat(timespec="milliseconds")
            request.state.x_request_datetime = request_timestamp
            response: Response
            try:
                response = await route_handler(request)
            # re-raise
            except exceptions.JSONException:
                raise
            except Exception as exc:
                if isinstance(exc, ValidationException):
                    error = await parse(
                            exc=exc, 
                            service_code=self.service_code
                        )
                else:
                    _logger.error(exc, exc_info=True)
                    message = additional_message = None
                    if hasattr(exc, 'status_code')\
                        and hasattr(exc, 'case_code'):
                        status_code = exc.status_code
                        case_code = exc.case_code
                        if hasattr(exc, 'message'):
                            message = exc.message
                        if hasattr(exc, 'additional_message'):
                            additional_message = exc.additional_message
                    else:
                        status_code = codes.STATUS_CODE_500
                        case_code = codes.CASE_CODE_01
                    error = exceptions.ErrorMessage(
                            status_code=status_code,
                            service_code=self.service_code,
                            case_code=case_code,
                            message = message,
                            additional_message=additional_message
                        )
                response = SNAPResponse(
                        status_code=error.status_code,
                        content=dict(
                                responseCode=error.responseCode,
                                responseMessage=error.responseMessage
                            )
                    )
            # Add default timestamp, cache-control
            response_timestamp: str = datetime.now(tz)\
                                .isoformat(timespec="milliseconds")
            response.headers.update({
                    'x-timestamp': response_timestamp,
                    'cache-control': 'no-store'
                })
            # TODO: Logger
            return response
        return error_handler

async def parse(
        exc: ValidationException,
        service_code: str
    ) -> exceptions.ErrorMessage:
    """ Parse Error. SNAP bedakan antara missing field dan format value """
    status_code = codes.STATUS_CODE_400
    tmp = defaultdict(list)
    for e in exc.errors():
        tmp[e['type']].append(e)

    def _get_location(error: dict) -> str:
        """ Parse missing location, either di Header or Body """
        location: str = ''
        try:
            location = error['loc'][0] == 'header' \
                and error['loc'][1].replace('_', '-').title() \
                or error['loc'][1].replace('_', '-')
        except:
            pass
        return location

    # Cegatan pertama: content-type bukan JSON
    if list(filter(lambda e: 
            e['type'] == 'literal_error' \
            and e['loc'][0] == 'header' \
            and e['loc'][1] == 'content_type', 
            exc.errors()
        )):
        error = exceptions.ErrorMessage(
                status_code=status_code, 
                service_code=service_code, 
                case_code=codes.CASE_CODE_00, 
                additional_message=f"Content Type Should Be JSON"
            )
    # Sisanya
    else:
        error_fields = []
        error_values = []
        for error_type, errors in tmp.items():
            # Mandatory Field(s) is missing
            if error_type == 'missing':
                error_fields += list(map(_get_location, errors))
            # Format value
            # https://docs.pydantic.dev/latest/errors/validation_errors
            else:
                error_values += list(map(_get_location, errors))
        
        # field mandatory di Header atau Body ada yang kurang, priority #1
        if error_fields:
            error = exceptions.ErrorMessage(
                    status_code=status_code, 
                    service_code=service_code, 
                    case_code=codes.CASE_CODE_02, 
                    additional_message=f"[{', '.join(error_fields)}]"
                )
        # format field value salah
        elif error_values:
            error = exceptions.ErrorMessage(
                    status_code=status_code, 
                    service_code=service_code, 
                    case_code=codes.CASE_CODE_01,
                    additional_message=f"[{', '.join(error_values)}]"
                )
        # other, General Error
        else:
            status_code = codes.STATUS_CODE_500
            error = exceptions.ErrorMessage(
                    status_code=status_code, 
                    service_code=codes.SERVICE_CODE_GENERAL, 
                    case_code=codes.CASE_CODE_00
                )
    return error