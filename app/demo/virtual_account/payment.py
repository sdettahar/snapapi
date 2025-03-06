# -*- coding: utf-8 -*-
# SNAP-API App Demo Virtual Account: Payment
# Author: S Deta Harvianto <sdetta@gmail.com>

import logging
import sys
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.StreamHandler(sys.stdout))

from typing_extensions import Annotated
from asyncer import asyncify
from fastapi import APIRouter, Header, Request, Depends, Body

from snapapi import SNAPRoute
from snapapi.model.virtual_account.payment import (
        PaymentHeader,
        PaymentRequest,
        PaymentAmount,
        PaymentResponseBill,
        PaymentResponseData
    )
from snapapi.codes import SERVICE_CODE_VIRTUAL_ACCOUNT_PAYMENT
from snapapi.security.oauth2 import Oauth2ClientCredentials
from app.demo.setting import Cache, Crypto
from app.demo.billing import BillDemo
Bill = BillDemo(service_code=SERVICE_CODE_VIRTUAL_ACCOUNT_PAYMENT)


class VAPaymentOAuth2(SNAPRoute):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service_code = SERVICE_CODE_VIRTUAL_ACCOUNT_PAYMENT

router = APIRouter(route_class=VAPaymentOAuth2)
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
        '/snap/v1.0/transfer-va/payment',
        tags=['Virtual Account (Direct)'],
        summary='VA Payment',
        response_model=PaymentResponseData,
        response_model_exclude_none=True
    )
async def inquiry(
        access_token: Annotated[str, Depends(verify_token)],
        headers: Annotated[PaymentHeader, Header()],
        body: Annotated[PaymentRequest, Body()],
        request: Request
    ) -> PaymentResponseData:
    """
    Pembayaran tagihan berdasarkan Virtual Account (Direct), dimana
    management Pembayaran Billing oleh Customer dilakukan oleh 
    Backend (Odoo, Django, Laravel, Oracle, SAP dsb). 
    Bank/Payment Gateway melakukan Payment ke API ini berdasarkan nomor
    Virtual Account dan nominal Pembayaran.

    Status Response:

    |responseCode|responseMessage                        |
    |------------|---------------------------------------|
    |2002500     |Successful                             |
    |4002500     |Bad Request                            |
    |4002501     |Invalid Field Format + ' ' + [FIELD]   |
    |4002502     |Invalid Mandatory Field + ' ' + [FIELD]|
    |4012500     |Unauthorized + ' ' + {REASON}          |
    |4012501     |Invalid Token (B2B)                    |
    |4042512     |Bill Not Found                         |
    |4042514     |Paid Bill                              |
    |4042519     |Bill Expired                           |
    |4092500     |Conflict                               |
    |5002500     |General Error                          |
    |5002501     |Internal Server Error                  |
    |5002502     |External Server Error                  |
    |5042500     |Timeout                                |

    HTTP Status Code sesuai dengan 3 digit pertama dari `responseCode`.
    """
    request_headers: dict = headers.model_dump()
    request_body: dict = await request.json()
    account: str = body.virtualAccountNo.strip()
    payment_amount = float(body.paidAmount.value)
    
    #1 Check Signature
    await asyncify(Crypto.verify_signature_transactional)(
            path = '/snap/v1.0/transfer-va/payment',
            http_method = 'POST',
            access_token = access_token,
            request_headers = request_headers,
            request_body = request_body
        )
    
    #2 Cache
    await Cache.add(
            headers=request_headers,
            service_code=SERVICE_CODE_VIRTUAL_ACCOUNT_PAYMENT
        )
    
    #3 Billing
    bill: dict = await Bill.payment(account, payment_amount)
    paidAmount = PaymentAmount(
            value=body.paidAmount.value, 
            currency=body.paidAmount.currency
        )  
    virtualAccountData = PaymentResponseBill(
            partnerServiceId=body.partnerServiceId,
            customerNo=body.customerNo,
            virtualAccountNo=body.virtualAccountNo,
            virtualAccountName=bill['accountName'],
            paymentRequestId=body.paymentRequestId,
            paidAmount=paidAmount,
            billDetails=bill.get('billDetails', [])
        )
    return PaymentResponseData(
            virtualAccountData=virtualAccountData,
            additionalInfo=bill.get('additionalInfo', None)
        )