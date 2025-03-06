# -*- coding: utf-8 -*-
# SNAP-API Model: Payment
# Author: S Deta Harvianto <sdetta@gmail.com>

from pydantic import Field, field_validator

from typing import Literal, Union, List
from typing_extensions import Annotated
from annotated_types import Len

from snapapi.tools import datetime_string
from snapapi.model.virtual_account import inquiry


class PaymentHeader(inquiry.InquiryHeader):
    """ rename for future update Payment Header if any """
    pass


class PaymentCommon(inquiry.InquiryCommon):
    """ sama persis dengan Inquiry """
    pass


class PaymentAmount(inquiry.InquiryAmount):
    """ sama persis dengan Inquiry """
    pass


class PaymentBillAmount(PaymentAmount):
    """ sama persis dengan Inquiry. Rename ben ora bingung """
    pass


class PaymentAdditionalInfo(inquiry.InquiryRequestAdditionalInfo):
    """ sama persis dengan Inquiry """
    pass


class PaymentRequestCommon(inquiry.InquiryRequestCommon):
    paidAmount: PaymentAmount = Field(
            description='Nominal uang yang dibayarkan oleh Customer'
        )


class PaymentRequestBillDetails(inquiry.InquiryResponseBillDetails):
    """ sama persis dengan Inquiry """
    pass


class PaymentRequestAdditionalInfo(inquiry.InquiryRequestAdditionalInfo):
    """ sama persis dengan Inquiry """
    pass


class PaymentRequest(PaymentRequestCommon):
    trxDateTime: str = Field(
            default='', 
            description="Tanggal waktu sistem Bank internal dengan zona waktu,"\
            " yang mengikuti standar ISO-8601."
        )
    paymentRequestId: str = Field(
            description='Unique identifier. Jika pembayaran datang '\
            'dari proses Inquiry, nilai harus sama dengan inquiryRequestId'
        )
    hashedSourceAccountNo: str = Field(
            default='', 
            description='Nomor akun sumber di-hash'
        )
    billDetails: Annotated[
                List[PaymentRequestBillDetails], Len(max_length=24)
            ] = Field(
            default=[],
            description='Detail setiap Bill untuk VA multi Billing.'
        )
    additionalInfo: Union[PaymentRequestAdditionalInfo, None] = Field(
            default=None, 
            description='Additional information for custom use that are"\
            " not provided by SNAP'
        )

    @field_validator('trxDateTime', mode='after')
    @classmethod
    def verify_trxDateTime(cls, val: str)->str:
        return datetime_string(val)


class PaymentResponse(inquiry.InquiryResponse):
    """ Minimal Model yang digunakan untuk Response """
    responseCode: str = Field(
            default=f'2002500', 
            description="Kode respon, dengan 'service_code' '25'", 
            pattern=r"^[245][0-9]{6}$"
        )
    responseMessage: str = Field(
            default='Successful', 
            description='Deskripsi respon', 
            max_length=150
        )


class PaymentResponseReason(inquiry.InquiryResponseReason):
    """ sama persis dengan Inquiry """
    pass


class PaymentResponseBillDetails(PaymentRequestBillDetails):
    """ sama persis dengan `PaymentRequestBillDetails` """
    pass


class PaymentResponseCommon(PaymentCommon):
    virtualAccountName: str = Field(
            description='Nama Customer', 
            max_length=255
        )
    billDetails: Annotated[
                List[PaymentResponseBillDetails], Len(max_length=24)
            ] = Field(default=[],
            description='Detail setiap bill untuk VA multi billing.'
        )


class PaymentResponseBillDescription(inquiry.InquiryResponseBillDescription):
    """ sama persis dengan Inquiry """
    pass


class PaymentResponseBill(PaymentResponseCommon):
    paymentRequestId: str = Field(
            description="Sama dengan Payment Request", 
            max_length=128
        )
    paidAmount: PaymentAmount = Field(
            description='Nominal uang yang dibayarkan oleh Customer'
        )
    paymentFlagStatus: Union[Literal['00', '01', '02'], None] = Field(
            default=None, 
            description="'00': Success, '01': Failed, '02': Timeout"
        )
    paymentFlagReason: Union[PaymentResponseReason, None] = Field(
            default=None,
            description='Penjelasan status Payment dalam dua bahasa'
        )


class PaymentResponseAdditionalInfo(inquiry.InquiryResponseAdditionalInfo):
    """ sama persis dengan Inquiry """
    pass


class PaymentResponseData(PaymentResponse):
    virtualAccountData: PaymentResponseBill = Field(
            description='Detail data akun virtual'
        )
    additionalInfo: Union[PaymentResponseAdditionalInfo, None] = Field(
            default=None, 
            description='Informasi tambahan dari Partner'
        )