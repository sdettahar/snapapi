# -*- coding: utf-8 -*-
# SNAP-API OAuth2
# Author: S Deta Harvianto <sdetta@gmail.com>

from typing import Optional, Union, Dict

from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
from fastapi.openapi.models import OAuthFlowClientCredentials
from fastapi.security.oauth2 import OAuth2
from fastapi.security.utils import get_authorization_scheme_param
from fastapi import Request


class Oauth2ClientCredentials(OAuth2):
    """ Just get Header Key Authorization Bearer """
    def __init__(
            self, 
            tokenUrl: str = '', 
            scheme_name: Union[str, None] = None, 
            scopes: Union[Dict[str, str], None] = None, 
            auto_error: bool = False
        ) -> None:
        if not scopes:
            scopes = {}
            clientCredentials = OAuthFlowClientCredentials(
                    tokenUrl= tokenUrl, 
                    scopes=scopes
                )
            flows = OAuthFlowsModel(clientCredentials=clientCredentials)
        super().__init__(
                flows=flows,
                scheme_name=scheme_name,
                auto_error=auto_error
            )

    async def __call__(self, request: Request) -> Optional[str]:
        """ Verifikasi Access Token dilakukan di masing2 endpoint """
        authorization = request.headers.get("Authorization")
        _, param = get_authorization_scheme_param(authorization)
        return param