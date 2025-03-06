# -*- coding: utf-8 -*-
# SNAP-API Models: Bill
# Author: S Deta Harvianto <sdetta@gmail.com>

from typing import Union
from pydantic import BaseModel, Field, field_validator, ConfigDict


class BillAmount(BaseModel):
    model_config = ConfigDict(
            field_title_generator=lambda field_name, field_info: field_name
        )
    value: str = Field(
            description='Nominal Tagihan dengan 2 desimal. "\
            "Biasanya kebijakan Bank minimum pembayaran 10rb',
            pattern="^\d{1,}\.\d{2}$"
        )
    currency: str = Field(
            default='IDR', 
            description="Mata Uang (ISO 4217), contoh: 'IDR'", 
            pattern=r"^[A-Z]{3}$"
        )


class BillDescription(BaseModel):
    model_config = ConfigDict(
            field_title_generator=lambda field_name, field_info: field_name
        )
    english: str = Field(
            default='Success', 
            description='Keterangan singkat Tagihan dalam bahasa Inggris', 
            max_length=18
        )
    indonesia: str = Field(
            default='Sukses', 
            description='Keterangan singkat Tagihan dalam bahasa Indonesia', 
            max_length=18
        )


class BillDetail(BaseModel):
    model_config = ConfigDict(
            field_title_generator=lambda field_name, field_info: field_name
        )
    billCode: Union[str, None] = Field(
            default=None,
            min_length=2,
            max_length=2,
            description="Kode sequence (numeric) Tagihan untuk "\
            "pilihan customer. Mulai dari '01'"
        )
    billNo: Union[str, None] = Field(
            default=None,
            description='Nomor (numeric (?)) Tagihan Customer', 
            max_length=18
        )
    billName: Union[str, None] = Field(
            default=None,
            max_length=20,
            # FIXME: contoh di dokumen SNAP 'Bill A for Jan'
            description='Bill Name'
        )
    billDescription: Union[BillDescription, None] = Field(
            default=None,
            description='Deskripsi Tagihan singkat dua bahasa.'
        )
    billAmount: Union[BillAmount, None] = Field(description='Nominal Tagihan')

    @field_validator('billCode')
    @classmethod
    def check_bill_code(cls, value: str) -> str:
        try:
            assert value.isnumeric()
        except:
            raise ValueError('Isi string harus numeric')
        return value


    @field_validator('billName')
    @classmethod
    def check_bill_name(cs, value: str) -> str:
        """
        FIXME: Contoh di dokumen SNAP agak membingungkan,

        Description: Bill number from Partner
        Example: 123456789012345678

        Jaman sekarang, siapa yang pakai angka untuk nomor Invoice ya? ~_~

        Sementara pass aja dulu, silakan subclass dan replate method ini jika
        Bank/PG mewajibkan penomoran tagihan berdasarkan angka.
        """
        pass
        return value