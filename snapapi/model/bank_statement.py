# -*- coding: utf-8 -*-
# SNAP-API Models: Bank Statement
# Author: S Deta Harvianto <sdetta@gmail.com>

from pydantic import (
    BaseModel, 
    Field, 
    model_validator, 
    field_validator,
    ConfigDict
)
from typing import Dict, Any, Optional, List, Literal
from typing_extensions import Self
from datetime import datetime
from snapapi.model.headers import TransactionHeader
from snapapi.model.bill import BillAmount as Amount


class BankStatementHeader(TransactionHeader):
    x_partner_id: str = Field(
        description='Partner ID', 
        min_length=3, 
        max_length=36
    )
    channel_id: str = Field(
        description='Channel pembayaran sesuai dengan kode dari Bank', 
        max_length=5
    )

class BankStatementCommon(BaseModel):
    model_config = ConfigDict(
        field_title_generator=lambda field_name, field_info: field_name
    )

class BankStatementRequest(BankStatementCommon):
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

    fromDateTime: Optional[str] = Field(
        default=datetime.now().replace(
            day=1, 
            hour=0, 
            minute=0, 
            second=0
        ).astimezone().isoformat(timespec='seconds'),
        description='ISO 8601 datetime string until seconds with TZD',
        max_length=25
    )
    toDateTime: Optional[str] = Field(
        default=datetime.now().astimezone().isoformat(timespec='seconds'),
        description='ISO 8601 datetime string until seconds with TZD',
        max_length=25
    )
    additionnalInfo: Optional[dict] = Field(
        default=None,
        description="Additional information for custom use that are not "\
        "not provided by SNAP"
    )

class BankStatementAmount(Amount):
    dateTime: str = Field(
        description='ISO 8601 datetime string until seconds with TZD',
        max_length=25
    )

class BankStatementBalance(BankStatementCommon):
    amount: BankStatementAmount
    startingBalance: BankStatementAmount
    endingBalance: BankStatementAmount

class BankStatementEntry(BankStatementCommon):
    numberOfEntries: str
    amount: Amount

class BankStatementDetailBalanceAmount(BaseModel):
    amount: Amount

class BankStatementDetailBalance(BaseModel):
    startAmount: List[BankStatementDetailBalanceAmount]
    endAmount: List[BankStatementDetailBalanceAmount]

class BankStatementDetailData(BaseModel):
    detailBalance: Optional[BankStatementDetailBalance] = Field(
        default=None,
        description="Starting and Ending balance before and after transaction"
    )
    amount: Optional[Amount] = None
    originAmount: Optional[Amount] = None
    transactionDate: str = Field(
        description='ISO 8601 datetime string until seconds with TZD',
        max_length=25
    )
    remark: str = Field(
        description="Transaction remark",
        max_length=256
    )
    transactionId: Optional[str] = Field(
        default=None,
        description="Internal transaction identifier from publisher prespective"
    )
    type: Literal['CREDIT', 'DEBIT'] = Field(
        description="Transaction type, either 'CREDIT' or 'DEBIT'"
    )

    @field_validator('type', mode='before')
    @classmethod
    def upper_type(cls, value: str) -> str:
        return value.upper()

    transactionDetailStatus: Optional[str] = Field(
        default=None,
        description="Transaction detail indicator "\
        "(original transaction or or error correction) "\
        "SUCCESS / ERROR CORRECTION"
    )
    detailInfo: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional information for detail transaction"
    )


class BankStatementResponse(BankStatementCommon):
    responseCode: Optional[str] = Field(
        default='2001400',
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
    balance: Optional[BankStatementBalance] = Field(
        default=None,
        description="Starting and Ending balance before "\
        "the first/last transaction"
    )
    totalCreditEntries: Optional[BankStatementEntry] = Field(
        default=None,
        description="Total transaction amount with type = CREDIT"
    )
    totalDebitEntries: Optional[BankStatementEntry] = Field(
        default=None,
        description="Total transaction amount with type = DEBIT"
    )
    hasMore: Optional[Literal['Y', 'N']] = Field(
        default=None,
        description="Memberikan informasi apakah masih ada record yang "\
        "belum ditampilkan dalam rentang `fromDateTime` - `toDateTime`",
        max_length=1
    )
    lastRecordDateTime: Optional[str] = Field(
        default=None,
        description='ISO 8601 datetime string until seconds with TZD',
        max_length=25
    )
    detailData: List[BankStatementDetailData]
    additionalInfo: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional information for custom use that are not "\
        "not provided by SNAP"
    )