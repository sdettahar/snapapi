# -*- coding: utf-8 -*-
# SNAP-API HTTP Status Codes dan Service Codes
# Author: S Deta Harvianto <sdetta@gmail.com>

# HTTP STATUS CODE
STATUS_CODE_200: int = 200 # Successful
STATUS_CODE_202: int = 202 # Accepted -> async -> kasih link
STATUS_CODE_400: int = 400 # BadRequest
STATUS_CODE_401: int = 401 # AccessError
STATUS_CODE_403: int = 403 # TransactionError
STATUS_CODE_404: int = 404 # TransactionInvalid
STATUS_CODE_405: int = 405 # TransactionNotImplemented
STATUS_CODE_409: int = 409 # Conflict
STATUS_CODE_500: int = 500 # ServerError
STATUS_CODE_504: int = 504 # TimeOut
# ... dstnya NEXT

# SERVICE CODE
SERVICE_CODE_GENERAL: str = '00'
SERVICE_CODE_OAUTH2: str = '73'
SERVICE_CODE_VIRTUAL_ACCOUNT_INQUIRY: str = '24'
SERVICE_CODE_VIRTUAL_ACCOUNT_PAYMENT: str = '25'
# ... dstnya NEXT

# CASE CODE
CASE_CODE_00: str = '00'
CASE_CODE_01: str = '01'
CASE_CODE_02: str = '02'
CASE_CODE_03: str = '03'
CASE_CODE_04: str = '04'
CASE_CODE_05: str = '05'
CASE_CODE_06: str = '06'
CASE_CODE_07: str = '07'
CASE_CODE_08: str = '08'
CASE_CODE_09: str = '09'
CASE_CODE_10: str = '10'
CASE_CODE_11: str = '11'
CASE_CODE_12: str = '12'
CASE_CODE_13: str = '13'
CASE_CODE_14: str = '14'
CASE_CODE_15: str = '15'
CASE_CODE_16: str = '16'
CASE_CODE_17: str = '17'
CASE_CODE_18: str = '18'
CASE_CODE_19: str = '19'
CASE_CODE_20: str = '20'
CASE_CODE_21: str = '21'
CASE_CODE_22: str = '22'
CASE_CODE_23: str = '23'