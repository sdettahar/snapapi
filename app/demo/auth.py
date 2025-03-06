# -*- coding: utf-8 -*-
# SNAP-API App Demo: OAuth2
# Author: S Deta Harvianto <sdetta@gmail.com>

import logging
import sys
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.StreamHandler(sys.stdout))

from typing_extensions import Annotated
from asyncer import asyncify
from fastapi import APIRouter, Header, Request

from snapapi import SNAPRoute
from snapapi.model.oauth2 import (
        Oauth2Request, 
        Oauth2Response, 
        Oauth2HeaderRequest
    )
from snapapi.codes import SERVICE_CODE_OAUTH2
from app.setting import TOKEN_EXPIRE
from app.demo.setting import Crypto

class SNAPOAuth2(SNAPRoute):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service_code = SERVICE_CODE_OAUTH2

router = APIRouter(route_class=SNAPOAuth2)

@router.post(
        '/snap/v1.0/access-token/b2b', 
        tags=['OAuth2'], 
        summary="Access Token B2B",
        response_model=Oauth2Response
    )
async def access_token_b2b(
        headers: Annotated[Oauth2HeaderRequest, Header()], 
        body: Oauth2Request,
        request: Request
    ) -> Oauth2Response:
    """
    SNAP menggunakan OAuth 2.0 Client Credential Flow, 
    dimana untuk mendapatkan Access Token, harus melakukan request sbb:
        
        ```
        
        POST /snap/v1.0/access-token/b2b HTTP/1.1
        Host: server.example.com
        X-TIMESTAMP : DateTime with timezone (ISO-8601)
        X-CLIENT-KEY : client_id
        X-SIGNATURE : Signature Asymmetric
        Content-Type : application/json
        {
            "grantType": "client_credentials"
        }

        ```

    dimana:
    - X-CLIENT-KEY: berupa Client ID yang dibuat oleh API
    - X-TIMESTAMP : ISO 8601 format: 2022-04-21T17:34:52+07:00

    Untuk membuat Signature:

        SHA256withRSA(stringToSign)

    Format `stringToSign`:

        client_id + '|' + timestamp

    contoh:

        'XJAPE8888|2025-02-01T15:30:32.843+07:00'

    Bank membuat Asymmetric Signature dengan `stringToSign` tersebut, 
    menggunakan algorithma SHA256withRSA dengan Public Key yang sudah dibuat 
    di atas. String yang dihasilkan ditempatkan pada `X-SIGNATURE` 
    di dalam Header.

    API verifikasi `X-SIGNATURE` tersebut di atas dengan menggunakan 
    Public Key dari Bank. Jika sesuai, Access Token digenerate oleh API 
    kemudian dikirimkan sebagai Authorization Bearer Code untuk mengakses 
    Transactional API selanjutnya.

    Access Token menggunakan JWT, dengan algorithm Signature HS512.

    Payload:

        {
            'iat': iat,
            'exp': exp
        }
    
    - **iat**: int, issued datetime dalam format UNIX Timestamp
    - **exp**: int, expired datetime dalam format UNIX Timestamp

    Payload diatas sudah _opaque_ (tidak mencatumkan informasi private),
    sesuai dengan RFC6749 dan RFC6750.

    --------------------------------------------------------------------------

    Setelah sukses mendapatkan Access Token, maka untuk setiap request 
    API Transactional, tambahkan `X-Signature` di dalam HEADER.

    `X-Signature` dibuat dengan menandatangani `stringToSign` 
    menggunakan Symmetric Signature algorithma HMAC-SHA512.
        
    Format `stringToSign`

        HTTPMethod 
        + ":"
        + Pathname
        + ":" 
        + AccessToken 
        + ":" 
        + Lowercase(HexEncode(SHA-256(minify(RequestBody)))) 
        + ":" 
        + TimeStamp

    dimana komponennya:

    - **HTTPMethod**: POST
    - **Pathname**: `URL Pathname` 
        https://developer.mozilla.org/en-US/docs/Web/API/URL/pathname
    - **AccessToken**: Access Token dari `/snap/v1.0/access-token/b2b`
    - **Lowercase(HexEncode(SHA-256(minify(RequestBody))))**, 
        dimana komponennya sbb:

        - minify(RequestBody):  JSON RequestBody yang sudah diminify 
                                (menghilangkan spasi), kemudian
        - SHA-256:  minify(RequestBody) di atas dihash dengan menggunakan 
                    algorithma SHA-256, kemudian
        - hashed tersebut di-encode menjadi `HEX` dimana 
          string yang dihasilkan di-lowercase-kan
    
    - **Timestamp**: datetime string ISO 8601 sama dengan format `X-Timestamp`

    Setiap komponen Signature tersebut disatukan dengan `:` 
    sebagai delimiternya. 

    Setelah itu buat digest HMAC-SHA512 `stringToSign` tersebut:

        HMAC_SHA512(client_secret, stringToSign)

    dimana:
    - **HMAC-SHA512**: function untuk membuat HMAC-SHA512
    - **client_secret**: `Client Secret` yang telah diberikan oleh API
    - **stringToSign**: `stringToSign` tsb di atas.

    Kemudian pastikan encode HMAC digest yang dihasilkan dengan 
    menggunakan `Base64` encoding `utf-8`.

    Status Response:

    |respondeCode   |responseMessage                |
    |---------------|-------------------------------|
    |2007300        |Success                        |
    |4017300        |Unauthorized + ' ' + {REASON}  |
    |4017301        |Invalid Token (B2B)            |
    """
    request_headers = dict(headers)
    access_token = await asyncify(Crypto.create_access_token)(
            request_headers = request_headers,
            expires_in=TOKEN_EXPIRE
        )
    return Oauth2Response(
            accessToken=access_token,
            expiresIn=str(TOKEN_EXPIRE)
        )