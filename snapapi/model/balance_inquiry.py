# -*- coding: utf-8 -*-
# SNAP-API Models: Bank Statement
# Author: S Deta Harvianto <sdetta@gmail.com>

from pydantic import (
    BaseModel, 
    Field, 
    model_validator, 
    ConfigDict
)
from typing import Dict, Any, Optional, List, Literal
from typing_extensions import Self
from snapapi.model.headers import TransactionHeader
from snapapi.model.bill import BillAmount as Amount

STATUS = Literal['0001', '0002', '0003', '0004', '0006', '0007', '0009']

class BalanceInquiryHeader(TransactionHeader):
    x_partner_id: str = Field(
        description='Partner ID', 
        min_length=3, 
        max_length=36
    )
    channel_id: str = Field(
        description='Channel pembayaran sesuai dengan kode dari Bank', 
        max_length=5
    )

class BalanceInquiryCommon(BaseModel):
    model_config = ConfigDict(
        field_title_generator=lambda field_name, field_info: field_name
    )

class BalanceInquiryRequest(BalanceInquiryCommon):
    partnerReferenceNo: Optional[str] = Field(
        default=None,
        description='Transaction identifier on service',
        max_length=64
    )
    bankCardToken: Optional[str] = Field(
        default=None,
        description="Card token for payment. Mutual exclusive with `accountNo`",
        max_length=128
    )
    accountNo: Optional[str] = Field(
        default=None,
        description="Bank Account number. Mutual exclusive with `bankCardToken`",
        max_length=16
    )
    
    @model_validator(mode="after")
    def verify_mutual_exclusive(self) -> Self:
        if (self.bankCardToken and self.accountNo) \
            or (not self.bankCardToken and not self.accountNo):
            raise ValueError("Expected 'bankCardToken' or 'accountNo' "\
                "but not both.")
        return self

    balanceTypes: Optional[List[str]] = Field(
        default=None,
        description="Balance Types of this parameter doesn’t exist, "\
        "its mean to inquiry all Balance Type on the account"
    )
    additionnalInfo: Optional[dict] = Field(
        default=None,
        description="Additional information for custom use that are not "\
        "not provided by SNAP"
    )

class BalanceInquiryAccountInfo(BaseModel):
    balanceType: Optional[str] = Field(
        default=None,
        description="Account type name"
    )
    amount: Optional[Amount] = Field(
        default=None,
        description="Net amount of the transaction"
    )
    floatAmount: Optional[Amount] = Field(
        default=None,
        description="Amount of deposit that is not effective yet "\
        "(due to holiday, etc.)"
    )
    holdAmount: Optional[Amount] = Field(
        default=None,
        description="Hold amount that cannot be used"
    )
    availableBalance: Optional[Amount] = Field(
        default=None,
        description="Account balance that can be used for financial transaction"
    )
    ledgerBalance: Optional[Amount] = Field(
        default=None,
        description="Account balance at the beginning of each day"
    )
    currentMultilateralLimit: Optional[Amount] = Field(
        default=None,
        description="Credit limit of the account / plafon"
    )
    registrationStatusCode: Optional[STATUS] = Field(
        default=None,
        description="Customer registration status"
    )
    status: Optional[STATUS] = Field(
        default=None,
        description="Account Status"
    )

class BalanceInquiryResponse(BalanceInquiryCommon):
    responseCode: Optional[str] = Field(
        default='2001100',
        description='Response Code',
        max_length=7
    )
    responseMessage: Optional[str] = Field(
        default='Successful',
        description='Response Message',
        max_length=150
    )
    referenceNo: Optional[str] = Field(
        default=None,
        description="Transaction identifier on service provider system. " \
        "Must be filled upon successful transaction",
        max_length=64
    )
    partnerReferenceNo: Optional[str] = Field(
        default=None,
        description='Transaction identifier on service consumer system',
        max_length=64
    )
    accountNo: Optional[str] = Field(
        default=None,
        description='Registered account number',
        max_length=32
    )
    name: Optional[str] = Field(
        default=None,
        description="Customer Account Name",
        max_length=140
    )
    accountInfos: Optional[List[BalanceInquiryAccountInfo]] = Field(
        default=None,
        description=""
    )