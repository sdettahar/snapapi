# -*- coding: utf-8 -*-
# SNAP-API App Demo: Main
# Author: S Deta Harvianto <sdetta@gmail.com>

from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import Request
from fastapi.responses import PlainTextResponse
from fastapi.middleware.cors import CORSMiddleware

from snapapi import SNAPAPI, SNAPResponse
from app.demo.setting import Cache

app = SNAPAPI(
        title='SNAP-API Demo',
        version="0.1.1",
        docs_url=None,
        description="""
### Standar Nasional Open API Pembayaran Versi 1.0.2
> Flow Inbound (Direct): Bank -> API
""")

app.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost"],
        allow_credentials=True,
        allow_methods=["GET", "POST"],
        allow_headers=["*"]
    )

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(
        request: Request,
        exc: StarletteHTTPException
    ) -> SNAPResponse:
    """
    ** TODO ** 
    gimana caranya otomatis keregister begitu instantiate SNAP-API?
    Do:
    1.  Delete cache key X-External-ID, jika status_code >=500 sehingga 
        Transactional Request bisa diulang dengan X-External-ID yang sama
    2.  Error Response sesuai dengan standard SNAP
    """
    if exc.status_code >=500:
        await Cache.delete(
                headers=dict(request.headers),
                status_code=exc.status_code
            )
    return SNAPResponse(
            status_code=exc.status_code, 
            content=exc.detail,
            headers=exc.headers
        )

@app.get('/', 
        include_in_schema=False, 
        response_class=PlainTextResponse
    )
async def home():
    return 'API SNAP'

@app.get('/robot.txt',
        include_in_schema=False, 
        response_class=PlainTextResponse
    )
async def robot():
    return """User-agent: *\nDisallow: /"""

# Routers
from . import auth
from .virtual_account import inquiry, payment
app.include_router(auth.router)
app.include_router(inquiry.router)
app.include_router(payment.router)