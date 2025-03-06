# -*- coding: utf-8 -*-
# SNAP-API: Headers
# Author: S Deta Harvianto <sdetta@gmail.com>

from pydantic import (
        BaseModel,
        Field,
        field_validator,
        AliasGenerator,
        ConfigDict
    )

from snapapi.tools import datetime_string


class CommonHeader(BaseModel):
    model_config = ConfigDict(
            alias_generator=AliasGenerator(
                validation_alias=lambda field_name: 
                    field_name.replace('-', '_').lower(),
                alias=lambda field_name: field_name.replace('_', '-').title()
            )
        )
    x_timestamp: str = Field(
            description="ISO 8601 timezone delta, "\
            "contoh: '2021-11-29T09:22:18.172+07:00'"
        )

    @field_validator('x_timestamp', mode='after')
    @classmethod
    def check_x_timestamp(cls, value: str) -> str:
        return datetime_string(value)


class TransactionHeader(CommonHeader):
    x_signature: str = Field(description='Symmetric Signature HMAC-SHA512')
    x_external_id: str = Field(
            description='Unique ID per request dalam 1 hari', 
            min_length=5,
            max_length=36
        )