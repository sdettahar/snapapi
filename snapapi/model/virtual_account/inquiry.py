# -*- coding: utf-8 -*-
# SNAP-API Model: Inquiry
# Author: S Deta Harvianto <sdetta@gmail.com>

from pydantic import BaseModel, Field, field_validator, ConfigDict

from typing import Literal, Union, List
from typing_extensions import Annotated
from annotated_types import Len

from snapapi.model import bill
from snapapi.tools import datetime_string
from snapapi.model.headers import TransactionHeader


class InquiryHeader(TransactionHeader):
    """ Inquiry/Payment Header """
    x_partner_id: str = Field(
            description='Partner ID', 
            min_length=5, 
            max_length=36
        )
    channel_id: str = Field(
            description='Channel pembayaran sesuai dengan kode dari Bank', 
            max_length=5
        )


class InquiryCommon(BaseModel):
    """ Model minimal dan mandatory untuk transaksi Inquiry """
    model_config = ConfigDict(
            field_title_generator=lambda field_name, field_info: field_name
        )

    partnerServiceId: str = Field(
            description='Derivative of X- PARTNER- ID , atau Company Code,'\
                        ' 8 digit left padding space. Contoh: “  088899”.', 
            # biasanya Company Code setidaknya 5 digit
            min_length=5,
            max_length=8,
            pattern="^\s{0,3}\d{5,8}$"
        )
    customerNo: str = Field(
            description='Nomor unik per Customer, '\
                        'format data sesuai dengan masing-masing Bank/PG.',
            # min_length 5 di sini hanya untuk 'basa-basi', gak mungkin
            # customerNo cuma 1 digit
            min_length=5,
            max_length=20,
            pattern="\d{5,20}"
        )
    virtualAccountNo: str = Field(
            description='partnerServiceId (8 digit left padding space) '\
                        '+ customerNo (up to 20 digits) or virtualAccountNo)', 
            min_length=9,
            max_length=28,
            pattern="^\s{0,18}\d{9,28}$"
        )


class InquiryAmount(bill.BillAmount):
    """ sama persis dengan bill.BillAmount """
    pass


class InquiryRequestAdditionalInfo(BaseModel):
    """ 
    SNAP membebaskan masing-masing PJP (Bank atau PG) atau Pengguna Layanan
    untuk mendefinisikan isinya.
    """
    pass


class InquiryRequestCommon(InquiryCommon):
    channelCode: Union[int, None] = Field(
            default=None,
            description='Channel code berdasarkan ISO 18245', 
            le=9999
        )
    sourceBankCode: Union[str, None] = Field(
            default=None,
            description='Source account bank code, sesuai dengan format '\
            'masing-masing Bank/PG.', 
            max_length=3
        )
    additionalInfo: Union[InquiryRequestAdditionalInfo, None] = Field(
            default=None, 
            description='Additional information for '\
                        'custom use that are not provided by SNAP'
        )


class InquiryRequest(InquiryRequestCommon):
    """ 
    Model lengkap sehingga Bank bisa mengirimkan data tambahan jika ada. 
    """
    inquiryRequestId: str = Field(
            description='Unique identifier per Inquiry request',
            max_length=128
        )
    amount: Union[InquiryAmount, None] = Field(
            default=None, 
            description='Nominal uang yang dimasukkan oleh Customer'
        )
    trxDateInit: Union[str, None] = Field(
            default=None, 
            description="Tanggal waktu sistem Bank/PG internal dengan "\
            "zona waktu, yang mengikut standar ISO-8601. "\
            "Contoh hanya sampai detik saja '2025-03-05T11:03:57+07:00' "\
            "Contoh hingga micro detik, '2025-03-05T11:03:25.576955+07:00'"
        )
    passApp: Union[str, None] = Field(
            default=None, 
            description='Kunci dari pihak ketiga untuk mengakses API seperti '
            'client secret', 
            max_length=64
        )

    @field_validator('trxDateInit', mode='after')
    @classmethod
    def check_trxDateInit(cls, value: str)->str:
        return datetime_string(value)


class InquiryResponseReason(BaseModel):
    english: str = Field(
            default='Success', 
            description='Penjelasan status Inquiry dalam bahasa Inggris', 
            max_length=64
        )
    indonesia: str = Field(
            default='Sukses',
            description='Penjelasan status Inquiry dalam bahasa Indonesia',
            max_length=64
        )


class InquiryResponseBillDescription(bill.BillDescription):
    """ persis dengan bill.BillDescription """
    pass


class InquiryResponseBillDetails(bill.BillDetail):
    """ persis dengan bill.BillDetail """
    pass


class InquiryResponse(BaseModel):
    """ Minimal Model yang digunakan untuk Response """
    responseCode: str = Field(
            default=f'2002400', 
            description="Kode respon, dengan 'service_code' '24'", 
            pattern=r"^[245][0-9]{6}$"
        )
    responseMessage: str = Field(
            default='Successful', 
            description='Deskripsi respon', 
            min_length=10,
            max_length=150
        )


class InquryResponseCommon(InquiryCommon):
    virtualAccountName: str = Field(
            description='Nama Customer', 
            max_length=255
        )
    billDetails: Annotated[
                List[InquiryResponseBillDetails], 
                Len(max_length=24)
            ] = Field(
            default=[],
            description='Detail setiap bill untuk VA multi billing.'
        )


class InquiryResponseBill(InquryResponseCommon):
    """ Minimal model untuk Single Bill """
    inquiryRequestId: str = Field(
            description="Sama dengan Inquiry Request", 
            max_length=128
        )
    totalAmount: InquiryAmount = Field(description='Nominal Total Tagihan')
    inquiryStatus: Union[Literal['00', '01'], None] = Field(
            default=None,
            description="'00': Success, '01': Failed, '03': Timeout'"
        )
    inquiryReason: Union[InquiryResponseReason, None] = Field(
            default=None, 
            description='Penjelasan status Inquiry dalam dua bahasa'
        )


class InquiryResponseAdditionalInfo(BaseModel):
    """ 
    Optional Model. Khusus field `info1` digunakan Bank untuk 
    menampilkan informasi tambahan ke Customer 
    """
    info1: Union[str, None] = Field(
            default=None, 
            description='Informasi pada field ini akan ditampilkan '
            'sebagai informasi tambahan kepada customer', 
            max_length=20
        )
    info2: Union[str, None] = Field(
            default=None, 
            description='Informasi tambahan', 
            max_length=20
        )
    info3: Union[str, None] = Field(
            default=None, 
            description='Informasi tambahan', 
            max_length=20
        )
    info4: Union[str, None] = Field(
            default=None, 
            description='Informasi tambahan', 
            max_length=20
        )
    info5: Union[str, None] = Field(
            default=None, 
            description='Informasi tambahan', 
            max_length=20
        )


class InquiryResponseData(InquiryResponse):
    """ Model lengkap jika tidak terjadi error; sistem, transaction dll """
    virtualAccountData: InquiryResponseBill = Field(
            description='Detail data akun virtual'
        )
    additionalInfo: Union[InquiryResponseAdditionalInfo, None] = Field(
            default=None, 
            description='Informasi tambahan dari Partner'
        )