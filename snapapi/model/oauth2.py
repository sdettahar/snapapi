# -*- coding: utf-8 -*-
# SNAP-API Model: OAuth2
# Author: S Deta Harvianto <sdetta@gmail.com>

from pydantic import BaseModel, Field

from typing import Literal, Dict, Any, Union

from snapapi.model.headers import CommonHeader


class Oauth2HeaderRequest(CommonHeader):
    x_client_key: str = Field(description='Client ID')
    x_signature: str = Field(
            description='Asymetric Signature SHA256withRSA (PKCS#1 v1.5)'
        )

class Oauth2Response(BaseModel):
    responseCode: str = Field(default='2007300')
    responseMessage: str = Field(default='Successful')
    accessToken: str = Field(description='JWT Access Token')
    tokenType: Literal['BearerToken'] = Field(
            default='BearerToken', 
            description="Jenis Access Token. Selalu 'BearerToken'"
        )
    expiresIn: str = Field(
            default=f"899",
            description='Access Token expiration dalam detik'
        )
    

class Oauth2Request(BaseModel):
    """ Request Model """
    grantType: Literal['client_credentials']
    additionalInfo: Union[Dict[str, Any], None] = Field(
            default=None, 
            description='Informasi tambahan'
        )