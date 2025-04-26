# -*- coding: utf-8 -*-
# SNAP-API Exception
# Author: S Deta Harvianto <sdetta@gmail.com>

from collections import defaultdict
from fastapi.exceptions import ValidationException
from typing import Optional, Dict, Any, Union
from snapapi import codes


class SNAPException(Exception):
    """ Base Exception """
    status_code = codes.STATUS_CODE_500
    case_code = codes.CASE_CODE_00
    message = 'General Error'
    additional_message: Union[str, None] = None

    def __init__(self, message: Union[str, None] = None) -> None:
        if message is None:
            message = self.message
        if self.additional_message:
            message = f'{message} {self.additional_message}'
        super().__init__(message)


## 400
class BadRequest(SNAPException):
    """ 
    responseCode: 400xx00
    responseMessage: 'Bad Request'
    """
    status_code = codes.STATUS_CODE_400
    case_code = codes.CASE_CODE_00
    message = 'Bad Request'


class InvalidFieldFormat(BadRequest):
    """ 
    responseCode: 400xx00
    responseMessage: 'Invalid Field Format [FIELDS]'

    dimana FIELDS berupa Header Key atau Body Field
    """
    case_code = codes.CASE_CODE_01
    message = 'Invalid Field Format'

    def __init__(self, additional_message: str) -> None:
        if additional_message is not None:
            self.message = f'{self.message} {additional_message}'
        super().__init__(self.message)


class MissingMandatoryField(BadRequest):
    """ 
    responseCode: 400xx00
    responseMessage: 'Missing Mandatory Field [FIELDS]'

    dimana FIELDS berupa Header Key atau Body Field
    """
    case_code = codes.CASE_CODE_02
    message = 'Missing Mandatory Field'

    def __init__(self, additional_message: str) -> None:
        if additional_message is not None:
            self.message = f'{self.message} {additional_message}'
        super().__init__(self.message)


## 401
class AccessError(SNAPException):
    """
    responseCode: 401xx00
    responseMessage: 'Unauthorized'
    """
    status_code = codes.STATUS_CODE_401
    case_code = codes.CASE_CODE_00
    message = 'Unauthorized'


class AccessDenied(AccessError):
    """
    responseCode: 401xx00
    responseMessage: 'Unauthorized Access Denied'
    """
    additional_message = 'Access Denied'


class InvalidSignature(AccessError):
    """
    responseCode: 401xx00
    responseMessage: 'Unauthorized Invalid Signature'
    """
    additional_message = 'Signature'


class InvalidTokenB2B(AccessError):
    """
    responseCode: 401xx01
    responseMessage: 'Invalid Token (B2B)'
    """
    case_code = codes.CASE_CODE_01
    message = 'Invalid Token (B2B)'


class InvalidTokenB2C(AccessError):
    """
    responseCode: 401xx02
    responseMessage: 'Invalid Customer Token'
    """
    case_code = codes.CASE_CODE_02
    message = 'Invalid Customer Token'


class TokenNotFoundB2B(AccessError):
    """
    responseCode: 401xx03
    responseMessage: 'Token Not Found (B2B)'
    """
    case_code = codes.CASE_CODE_03
    message = 'Token Not Found (B2B)'


class TokenNotFoundB2C(AccessError):
    """
    responseCode: 401xx04
    responseMessage: 'Customer Token Not Found'
    """
    case_code = codes.CASE_CODE_04
    message = 'Customer Token Not Found'


## 403
class TransactionError(SNAPException):
    """
    **TODO** status code 403
    """
    status_code = codes.STATUS_CODE_403
    message = 'Transaction Error'


## 404
class TransactionInvalid(SNAPException):
    """
    responseCode: 404xx00
    responseMessage: 'Invalid Transaction Status'
    """
    status_code = codes.STATUS_CODE_404
    case_code = codes.CASE_CODE_00
    message = 'Invalid Transaction Status'


class AccountNotFound(TransactionInvalid):
    """
    responseCode: 404xx11
    responseMessage: 'Account Not Found'
    """
    case_code = codes.CASE_CODE_11
    message = 'Account Not Found'


class VirtualAccountNotFound(AccountNotFound):
    """
    responseCode: 404xx11
    responseMessage: 'Virtual Account Not Found'
    """
    message = 'Virtual Account Not Found'


class BillNotFound(TransactionInvalid):
    """
    responseCode: 404xx12
    responseMessage: 'Bill Not Found'
    """
    case_code = codes.CASE_CODE_12
    message = 'Bill Not Found'


class InvalidAmount(TransactionInvalid):
    """
    responseCode: 404xx13
    responseMessage: 'Invalid Amount'
    """
    case_code = codes.CASE_CODE_13
    message = 'Invalid Amount'


class BillPaid(TransactionInvalid):
    """
    responseCode: 404xx14
    responseMessage: 'Bill is Paid'
    """
    case_code = codes.CASE_CODE_14
    message = 'Bill is Paid'


class InconsistentRequest(TransactionInvalid):
    """
    responseCode: 404xx18
    responseMessage: 'Inconsistent Request'
    """
    case_code = codes.CASE_CODE_18
    message = 'Inconsistent Request'


class BillExpired(TransactionInvalid):
    """
    responseCode: 404xx19
    responseMessage: 'Bill is Expired'
    """
    case_code = codes.CASE_CODE_19
    message = 'Bill is Expired'


## 409
class TransactionConflict(SNAPException):
    """
    responseCode: 409xx00
    responseMessage: 'Conflict'
    """
    status_code = codes.STATUS_CODE_409
    case_code = codes.CASE_CODE_00
    message = 'Conflict'


## 500
class ServerError(SNAPException):
    """
    responseCode: 500xx00
    responseMessage: 'General Error'
    """
    pass


class InternalServerError(ServerError):
    """
    responseCode: 500xx01
    responseMessage: 'Internal Server Error'
    """
    case_code = codes.CASE_CODE_01
    message = 'Internal Server Error'


class ExternalServerError(ServerError):
    """
    responseCode: 500xx02
    responseMessage: 'External Server Error'
    """
    case_code = codes.CASE_CODE_02
    message = 'External Server Error'


## 505
class TimeOut(SNAPException):
    """
    responseCode: 504xx00
    responseMessage: 'Time Out'
    """
    status_code = codes.STATUS_CODE_504
    case_code = codes.CASE_CODE_00
    message = 'Time Out'


async def parse_validation_exception(exc: ValidationException) -> SNAPException:
    """ Parse Error. SNAP bedakan antara missing field dan format value """
    status_code = codes.STATUS_CODE_400
    tmp = defaultdict(list)
    for e in exc.errors():
        tmp[e['type']].append(e)

    def _get_location(error: dict) -> str:
        """ Parse missing location, either di Header or Body """
        location: str = ''
        try:
            location = error['loc'][0] == 'header' \
                and error['loc'][1].replace('_', '-').title() \
                or error['loc'][1].replace('_', '-')
        except:
            pass
        return location

    # Cegatan pertama: content-type bukan JSON
    if list(filter(lambda e: 
            e['type'] == 'literal_error' \
            and e['loc'][0] == 'header' \
            and e['loc'][1] == 'content_type', 
            exc.errors()
        )):
        return BadRequest('Content Type Should Be JSON')
    # Sisanya
    else:
        error_fields = []
        error_values = []
        for error_type, errors in tmp.items():
            # Mandatory Field(s) is missing
            if error_type == 'missing':
                error_fields += list(map(_get_location, errors))
            # Format value
            # https://docs.pydantic.dev/latest/errors/validation_errors
            else:
                error_values += list(map(_get_location, errors))
        # field mandatory di Header atau Body ada yang kurang, priority #1
        if error_fields:
            return MissingMandatoryField(f"[{', '.join(error_fields)}]")
        # format field value salah
        elif error_values:
            return InvalidFieldFormat(f"[{', '.join(error_values)}]")
        # other
        else:
            return BadRequest()