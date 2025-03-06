# -*- coding: utf-8 -*-
# SNAP-API Response
# Author: S Deta Harvianto <sdetta@gmail.com>

try:
    import orjson
    has_orjson = True
except ModuleNotFoundError:
    import json
    has_orjson = False

from datetime import datetime, timezone, tzinfo
from typing import Optional, Any, Mapping

from starlette.responses import Response as StarletteResponse
from starlette.background import BackgroundTask


class SNAPResponse(StarletteResponse):
    """ 
    Add X-Timestamp di setiap Response 

    TODO: totally replace starlette.responses
    """
    def __init__(
        self,
        content: Any,
        status_code: int = 200,
        headers: Optional[Mapping[str, str]] = None,
        media_type: Optional[str] = None,
        background: Optional[BackgroundTask] = None
    ) -> None:
        super().__init__(content, status_code, headers, media_type, background)
        if not self.headers:
            headers = dict()
        tz: Optional[tzinfo] = datetime.now().astimezone().tzinfo
        timestamp: str = datetime.now(tz).isoformat(timespec="milliseconds")
        self.headers.update({
                'x-timestamp': timestamp,
                'cache-control': 'no-store'
            })

    def render(self, content: Any) -> bytes:
        return has_orjson \
            and orjson.dumps(content, 
                    option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY
                )\
            or json.dumps(
                    content,
                    ensure_ascii=False,
                    allow_nan=False,
                    indent=None,
                    separators=(',', ':'),
                ).encode('utf-8')