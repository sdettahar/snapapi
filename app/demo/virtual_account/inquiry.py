# -*- coding: utf-8 -*-
# SNAP-API App Demo Virtual Account: Inquiry
# Author: S Deta Harvianto <sdetta@gmail.com>

import logging
import sys
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.StreamHandler(sys.stdout))

from typing_extensions import Annotated
from asyncer import asyncify
from fastapi import APIRouter, Header, Request, Depends, Body

from snapapi import SNAPRoute
from snapapi.model.virtual_account.inquiry import (
        InquiryHeader,
        InquiryRequest,
        InquiryResponseBill,
        InquiryResponseData
    )
from snapapi.codes import SERVICE_CODE_VIRTUAL_ACCOUNT_INQUIRY
from snapapi.security.oauth2 import Oauth2ClientCredentials

from app.demo.setting import Cache, Crypto
from app.demo.billing import BillDemo
Bill = BillDemo(service_code=SERVICE_CODE_VIRTUAL_ACCOUNT_INQUIRY)


class VAInquiryOAuth2(SNAPRoute):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service_code = SERVICE_CODE_VIRTUAL_ACCOUNT_INQUIRY

router = APIRouter(route_class=VAInquiryOAuth2)
oauth2_scheme = Oauth2ClientCredentials(
        # FIXME: harusnya ini endpoint buat dapetin Token dari Swagger
        # tapi kok Form?
        tokenUrl='/snap/v1.0/access-token/b2b'
    )
async def verify_token(
        access_token: Annotated[str, Depends(oauth2_scheme)]
    ) -> str:
    await asyncify(Crypto.verify_access_token)(access_token)
    return access_token

@router.post(
        '/snap/v1.0/transfer-va/inquiry',
        tags=['Virtual Account (Direct)'],
        summary='VA Inquiry',
        response_model=InquiryResponseData,
        response_model_exclude_none=True
    )
async def inquiry(
        access_token: Annotated[str, Depends(verify_token)],
        headers: Annotated[InquiryHeader, Header()],
        body: Annotated[InquiryRequest, Body()],
        request: Request
    ) -> InquiryResponseData:
    """ 
    Informasi tagihan berdasarkan Virtual Account (Direct), dimana
    management nomor Virtual Account, Billing dan Customer dilakukan oleh 
    Backend (Odoo, Django, Laravel, Oracle, SAP dsb). 
    Bank/Payment Gateway melakukan Inquiry ke API ini berdasarkan nomor
    Virtual Account.

    Status Response:

    |responseCode|responseMessage                        |
    |------------|---------------------------------------|
    |2002400     |Successful                             |
    |4002400     |Bad Request                            |
    |4002401     |Invalid Field Format + ' ' + [FIELD]   |
    |4002402     |Invalid Mandatory Field + ' ' + [FIELD]|
    |4012400     |Unauthorized + ' ' + {REASON}          |
    |4012401     |Invalid Token (B2B)                    |
    |4042412     |Bill Not Found                         |
    |4042414     |Paid Bill                              |
    |4042419     |Bill Expired                           |
    |4092400     |Conflict                               |
    |5002400     |General Error                          |
    |5002401     |Internal Server Error                  |
    |5002402     |External Server Error                  |
    |5042400     |Timeout                                |

    HTTP Status Code sesuai dengan 3 digit pertama dari `responseCode`
    """
    request_headers: dict = headers.model_dump()
    request_body: dict = await request.json()
    account: str = body.virtualAccountNo.strip()

    #1 Check Signature
    await asyncify(Crypto.verify_signature_transactional)(
            path = '/snap/v1.0/transfer-va/inquiry',
            http_method = 'POST',
            access_token = access_token,
            request_headers = request_headers,
            request_body = request_body
        )
    
    #2 Cache
    await Cache.add(
            headers=request_headers,
            service_code=SERVICE_CODE_VIRTUAL_ACCOUNT_INQUIRY
        )
    
    #3 Billing
    bill: dict = await Bill.inquiry(account)
    virtualAccountData = InquiryResponseBill(
            partnerServiceId=body.partnerServiceId,
            customerNo=body.customerNo,
            virtualAccountNo=body.virtualAccountNo,
            virtualAccountName=bill['accountName'],
            inquiryRequestId=body.inquiryRequestId,
            totalAmount=bill['totalAmount'],
            # Opsional
            billDetails=bill.get('billDetails', [])
        )
    return InquiryResponseData(
            virtualAccountData=virtualAccountData,
            additionalInfo=bill.get('additionalInfo', None)
        )