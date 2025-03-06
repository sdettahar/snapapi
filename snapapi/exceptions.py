# -*- coding: utf-8 -*-
# SNAP-API Exception
# Author: S Deta Harvianto <sdetta@gmail.com>

import logging
import sys
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.StreamHandler(sys.stdout))

from typing import Optional, Dict, Any, Union

from fastapi import HTTPException as FastAPIHTTPException

from snapapi import codes


class JSONException(FastAPIHTTPException):
    """
    JSONException yang mengadopsi Error Response SNAP 

    FIXME: lepas dari fastapi bisa harusnya
    """
    def __init__(
            self, 
            status_code: int, 
            service_code: str, 
            case_code: str = codes.CASE_CODE_00,
            message: Union[str, None] = None,
            additional_message: Union[str, None] = None,
            detail: Any = None, 
            headers: Optional[Dict[str, str]] = None
        ) -> None:
        # TODO: Logger
        try:
            error = ErrorMessage(
                    status_code=status_code,
                    service_code=service_code,
                    case_code=case_code,
                    message=message,
                    additional_message=additional_message
                )
        except Exception as exc:
            # Exception of Exception ~_~
            _logger.error(exc, exc_info=True)
            status_code = codes.STATUS_CODE_500
            error = ErrorMessage(
                    status_code=status_code,
                    service_code=service_code,
                    case_code=codes.CASE_CODE_01
                )
        super().__init__(
                status_code=status_code,
                detail=dict(error),
                headers=headers
            )


class SNAPException(Exception):
    status_code = None
    case_code = None
    additional_message: Union[str, None] = None
    def __init__(
            self,
            msg: Union[str, None] = None,
            /,
            *,
            status_code: Union[int, None] = status_code,
            case_code: Union[str, None] = case_code,
            additional_message: Union[str, None] = additional_message
        ) -> None:
        if status_code is not None:
            self.status_code = status_code
        if case_code is not None:
            self.case_code = case_code
        if additional_message is not None:
            self.additional_message = additional_message
        super().__init__(msg)


class AccessError(SNAPException):
    """ 401xx00 """
    status_code = codes.STATUS_CODE_401
    case_code = codes.CASE_CODE_00
    message = 'Unauthorized'
    additional_message: Union[str, None] = None

    def __init__(self, msg: Union[str, None] = None, /) -> None:
        if msg is not None:
            message = msg
        else:
            message = self.message
        additional_message = msg
        super().__init__(
                message,
                status_code=self.status_code,
                case_code=self.case_code,
                additional_message=additional_message
            )


class AccessDenied(AccessError):
    """ 401xx00 """
    additional_message = 'Access Denied'
    
    def __init__(self) -> None:
        super().__init__(self.additional_message)


class InvalidSignature(AccessError):
    """ 401xx00 """
    additional_message = 'Invalid Signature'

    def __init__(self) -> None:
        super().__init__(self.additional_message)


class AccessTokenNotFound(AccessError):
    """ 401xx00 """
    additional_message = 'Access Token Not Found'

    def __init__(self) -> None:
        super().__init__(self.additional_message)


class AccessTokenInvalid(AccessError):
    """ 401xx00 """
    additional_message = 'Access Token Invalid'

    def __init__(self) -> None:
        super().__init__(self.additional_message)


class TransactionError(SNAPException):
    """ 403xxyy **TODO** case_code per 403 """
    status_code = codes.STATUS_CODE_403


class TransactionInvalid(SNAPException):
    """ 404xx00, 
    default message:  'Invalid Transaction Status' 

    Note: 404 tidak ada additional_message
    """
    status_code = codes.STATUS_CODE_404
    case_code = codes.CASE_CODE_00
    message = 'Invalid Transaction Status'

    def __init__(
            self, 
            msg: Union[str, None] = None,
            /
        ) -> None:
        if msg is None:
            message = self.message
        else:
            message = msg
            self.message = msg
        super().__init__(
                message,
                status_code=self.status_code,
                case_code=self.case_code
            )


class AccountNotFound(TransactionInvalid):
    """ 404xx12, 
    default message: 'Account Not Found' 

    Custom Message:
        
        ```python

        >>> raise AcccountNotFound('Virtual')
        AccountNotFound: Virtual Account Not Found

        >>> raise AcccountNotFound('Credit Card')
        AccountNotFound: Credit Card Account Not Found

        dstnya ..

        ```
    """
    case_code = codes.CASE_CODE_12
    message = 'Account Not Found'

    def __init__(
            self,
            msg: Union[str, None] = None,
        ) -> None:
        if msg is not None:
            message = f'{msg} {self.message}'

        else:
            message = self.message
        super().__init__(message)


class VirtualAccountNotFound(AccountNotFound):
    """ shortcut to AccountNotFound('Virtual') """
    def __init__(self) -> None:
        super().__init__('Virtual')


class BillNotFound(TransactionInvalid):
    """ 404xx12, fix message: 'Bill Not Found' """
    case_code = codes.CASE_CODE_12

    def __init__(self) -> None:
        super().__init__('Bill Not Found')


class BillInvalidAmount(TransactionInvalid):
    """ 404xx13, fix message: 'Invalid Amount' """
    case_code = codes.CASE_CODE_13
    
    def __init__(self) -> None:
        super().__init__('Invalid Amount')


class BillPaid(TransactionInvalid):
    """ 404xx14, fix message: 'Paid Bill' """
    case_code = codes.CASE_CODE_14

    def __init__(self) -> None:
        super().__init__('Paid Bill')


class BillExpired(TransactionInvalid):
    """ 404xx19, fix message: 'Bill Expired' """
    case_code = codes.CASE_CODE_19

    def __init__(self) -> None:
        super().__init__('Bill Expired')


class TransactionConflict(TransactionInvalid):
    """ 409xx00, fix message: 'Conflict' """
    status_code = codes.STATUS_CODE_409

    def __init__(self) -> None:
        super().__init__('Conflict')


class ExternalServerError(SNAPException):
    """ 500xx02, optional message, misal: 'Billing Backend' """
    status_code = codes.STATUS_CODE_500
    case_code = codes.CASE_CODE_02

    def __init__(
            self, 
            message: Union[str, None] = None
        ) -> None:
        if message is not None:
            additional_message = message
        else:
            additional_message = None
        super().__init__(message, additional_message=additional_message)


class TimeOut(SNAPException):
    """ 504xx00, fix message: 'Time Out' """
    status_code = codes.STATUS_CODE_504
    case_code = codes.CASE_CODE_00

    def __init__(self) -> None:
        super().__init__('Time Out')


class ErrorMessage:
    """ Parse Error Response Status sesuai dengan SNAP """
    def __init__(
            self, 
            status_code: int = codes.STATUS_CODE_500, 
            service_code: str = codes.SERVICE_CODE_GENERAL, 
            case_code: str = codes.CASE_CODE_00, 
            message: Union[str, None] = None,
            additional_message: Union[str, None] = None
        ) -> None:
        """ 
        Error Code dan Message sesuai dengan standard SNAP 
            
            :param status_code:         int, 
                                        HTTP STATUS Code
            :param service_code:        str(2), 
                                        Service Code, contoh '73' untuk OAuth2
            :param case_code:           str(2), default '00', 
                                        Case Code mengacu pada SNAP
            :param additional_message:  str, opsional, 
                                        Informasi tambahan
        """
        if not isinstance(status_code, int):
            raise TypeError('status_code must be int')
        if not isinstance(service_code, str):
            raise TypeError('service_code must be str')
        if not len(service_code) == 2:
            raise ValueError('Panjang karakter service_code harus 2')

        if status_code == codes.STATUS_CODE_400:
            responseMessage = self._status_400(
                    case_code=case_code, 
                    message=message, 
                    additional_message=additional_message
                )
        elif status_code == codes.STATUS_CODE_401:
            responseMessage = self._status_401(
                    case_code=case_code, 
                    message=message,
                    additional_message=additional_message
                )
        elif status_code == codes.STATUS_CODE_404:
            responseMessage = self._status_404(
                                    case_code=case_code, 
                                    message=message
                                )
        elif status_code == codes.STATUS_CODE_409:
            message = 'Conflict'
            responseMessage = additional_message \
                              and f'{message} {additional_message}'\
                              or message
        elif status_code == codes.STATUS_CODE_500:
            responseMessage = self._status_500(case_code, 
                                additional_message)
        elif status_code == codes.STATUS_CODE_504:
            responseMessage = 'Timeout'
        else:
            raise ValueError(f'HTTP Status Code Not Implemented: {status_code}')

        self.status_code = status_code
        self.service_code = service_code
        self.case_code = case_code
        self.responseCode = f'{status_code}{service_code}{case_code}'
        self.responseMessage = responseMessage

    def __str__(self) -> str:
        return ', '.join(
                f"{k}={v}" if not isinstance(v, str) else f"{k}='{v}'" 
                for k, v in self.__dict__.items()
            )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.__str__()})"

    def __call__(self) -> Dict[str, str]:
        return self.__dict__

    def __iter__(self):
        return iter(self.__dict__.items())

    def _status_400(
            self, 
            case_code: str, 
            message: Union[str, None] = None, 
            additional_message: Union[str, None] = None
        ) -> str:
        ''' responseMessage HTTP Status Code 400 per Case '''
        if not isinstance(case_code, str):
            raise TypeError('case_code harus str')
        if not len(case_code) == 2:
            raise ValueError('Panjang karakter case_code harus 2')

        if case_code == codes.CASE_CODE_00:
            message_default = 'Bad Request'
            return additional_message \
                and f'{message_default} {additional_message}' \
                or message_default
        elif case_code == codes.CASE_CODE_01:
            if not additional_message:
                raise NameError('additional_message is mandatory')
            return f"{message or 'Invalid Field Format'}"\
                   f' {additional_message}'
        elif case_code == codes.CASE_CODE_02:
            if not additional_message:
                raise NameError('additional_message is mandatory')
            return f"{message or 'Missing Mandatory Field'}"\
                   f' {additional_message}'
        else:
            raise ValueError(f'Case Code Not Implemented: {case_code}')

    def _status_401(
            self, 
            case_code: str, 
            message: Union[str, None] = None, 
            additional_message: Union[str, None] = None
        ) -> str:
        ''' responseMessage HTTP Status Code 401 per Case '''
        if not isinstance(case_code, str):
            raise TypeError('case_code harus str')
        if not len(case_code) == 2:
            raise ValueError('Panjang karakter case_code harus 2')
        
        message_default = 'Unauthorized'
        if case_code == codes.CASE_CODE_00:
            msg = f"{message or message_default}"
            return additional_message \
               and f'{msg} {additional_message}' \
               or msg
        elif case_code == codes.CASE_CODE_01:
            msg = f"{message or 'Invalid Token (B2B)'}"
            return additional_message \
               and f'{msg} {additional_message}' \
               or msg
        elif case_code == codes.CASE_CODE_02:
            # FIXME: belum terpakai kayaknya, utk B2C
            return message or 'Invalid Customer Token'
        elif case_code == codes.CASE_CODE_03:
            return message or 'Token Not Found (B2B)'
        else:
            raise ValueError(f'Case Code Not Implemented: {case_code}')

    def _status_404(
            self,
            case_code: str,
            message: Union[str, None] = None
        ) -> str:
        ''' responseMessage HTTP Status Code 404 per Case '''
        if not isinstance(case_code, str):
            raise TypeError('case_code harus str')
        if not len(case_code) == 2:
            raise ValueError('Panjang karakter case_code harus 2')

        if case_code == codes.CASE_CODE_00:
            return 'Invalid Transaction Status'
        elif case_code == codes.CASE_CODE_12:
            return message or 'Bill Not Found'
        elif case_code == codes.CASE_CODE_13:
            return message or 'Invalid Amount'
        elif case_code == codes.CASE_CODE_14:
            return message or 'Paid Bill'
        elif case_code == codes.CASE_CODE_19:
            return message or 'Bill Expired'
        else:
            raise NotImplementedError(
                    f'Case Code Not Implemented: {case_code}'
                )

    def _status_500(
            self,
            case_code: str,
            additional_message: Union[str, None] = None
        ) -> str:
        ''' responseMessage HTTP Status Code 500 '''
        if not isinstance(case_code, str):
            raise TypeError('case_code harus str')
        if not len(case_code) == 2:
            raise ValueError('Panjang karakter case_code harus 2')

        if case_code == codes.CASE_CODE_00:
            return 'General Error'
        elif case_code == codes.CASE_CODE_01:
            message = 'Internal Server Error'
            return additional_message \
               and f'{message}: {additional_message}' \
               or message
        elif case_code == codes.CASE_CODE_02:
            message = 'External Server Error'
            return additional_message \
               and f'{message}: {additional_message}' \
               or message
        else:
            raise NotImplementedError(
                    f'Case Code Not Implemented: {case_code}'
                )