# -*- coding: utf-8 -*-
# SNAP-API Test Demo
# Author: S Deta Harvianto <sdetta@gmail.com>

import os
import functools
import argparse
import requests
import json
import hashlib
import secrets
import sys
sys.path.insert(1, '..')

from pathlib import Path
from configparser import ConfigParser
from datetime import datetime, timezone
from timeit import default_timer as timer
from shlex import quote
from Crypto.PublicKey import RSA

from snapapi.security.crypto import SNAPCrypto

HOMEDIR = Path.home()
CONFIG_PATH = HOMEDIR / '.snapapi'
CONFIG_FILE = CONFIG_PATH / 'snapapi.conf'

try:
    if oct(CONFIG_FILE.stat().st_mode)[-3:] != '600':
        raise SystemError(f"{CONFIG_FILE} permission harus diset 600 "\
    f"""

    contoh:
    $ chmod 600 {CONFIG_FILE}
    
    """)

    with open(CONFIG_FILE) as file:
        config_contents: str = file.read()

except FileNotFoundError:
    raise FileNotFoundError(f"File {str(CONFIG_FILE)} belum dibuat.")
except Exception as exc:
    raise exc

config = ConfigParser()
config.read_string(config_contents)

NAMESPACE = 'demo'
CLIENT_ID = config[NAMESPACE]['client_id']
CLIENT_SECRET = config[NAMESPACE]['client_secret']

private_key_file = CONFIG_PATH / f'{NAMESPACE}.key.pem'
if oct(private_key_file.stat().st_mode)[-3:] != '600':
    raise SystemError(f"{private_key_file} permission harus diset 600")

with open(private_key_file, 'rb') as private_key:
    PRIVATE_KEY = private_key.read()

Crypto = SNAPCrypto(
        client_id = CLIENT_ID,
        client_secret = CLIENT_SECRET,
        private_key = PRIVATE_KEY
    )


def to_curl(request: requests.PreparedRequest) -> str:
    """ Taken from https://github.com/ofw/curlify """
    parts = [('curl', None), ('-X', request.method)]
    parts += [('', f'{request.url}\n')]

    for k, v in sorted(request.headers.items()):
        parts += [('-H', '{0}: {1}\n'.format(k, v))]

    if request.body:
        body = request.body
        if isinstance(body, bytes):
            body = body.decode('utf-8')
        body = json.dumps(json.loads(body), indent=2)
        parts += [('-d', body)]

    flat_parts = []
    for a, b in parts:
        if a:
            flat_parts.append(quote(a))
        if b:
            flat_parts.append(quote(b))
    return ' '.join(flat_parts)


def create_certificate(namespace: str) -> None:
    ''' 
    Create self-signed Certificate. Filename sesuai dengan namespace.
    
    Implementasi di lapangan:

    Jika flow API adalah API --> Bank,
    maka anda akan membutuhkan Private Key untuk membuat Signature OAuth2.
    Public Certificate dibutuhkan oleh Bank untuk memverifikasi Signature tsb.

    Jika flow API adalah Bank --> API,
    maka anda membutuhkan Public Certificate yang dibuat oleh Bank 
    untuk memverifikasi Signature Oauth2 dari Bank.

    Tool ini hanya digunakan sebagai test saat develop aplikasi API.
    '''
    namespace = namespace.lower()
    key = RSA.generate(2048)
    private_key = key.exportKey()
    public_cert = key.publickey().exportKey()
    # Private Key
    key_pem_path = CONFIG_PATH / f'{namespace}.key.pem'
    key_pem_path.write_bytes(private_key);
    key_pem_path.chmod(0o600)
    # Public Cert
    public_pem_path = CONFIG_PATH / f'{namespace}.cert.pem'
    public_pem_path.write_bytes(public_cert);
    public_pem_path.chmod(0o600)



VIRTUAL_ACCOUNT = '1234506000009587' # open
# VIRTUAL_ACCOUNT = '1234505000001234' # paid
# VIRTUAL_ACCOUNT = '1234505000005678' # expired
# VIRTUAL_ACCOUNT = '1234505000008984' # no bill
# VIRTUAL_ACCOUNT = '1234505000118984' # no VA
PAID_AMOUNT = 103500.0
timing = []

session = requests.Session()

def get_access_token(host: str)->requests.Response:
    timestamp = datetime.now(timezone.utc).astimezone()\
                .isoformat(timespec='milliseconds')
    string_to_sign = f'{CLIENT_ID}|{timestamp}'.encode()
    oauth2_signature = Crypto.create_signature_oauth2(string_to_sign)
    request_headers = {
            'CONTENT-TYPE': 'application/json',
            'X-CLIENT-KEY': CLIENT_ID,
            # 'X-CLIENT-KEY': 'CLIENT_ID',
            'X-TIMESTAMP': timestamp,
            'X-SIGNATURE': oauth2_signature,
            # 'X-SIGNATURE': 'aaaaaaaaaaaaaaaaaaaaaaa',
            'Cache-Control': 'no-cache'
        }
    request_body = {
            "grantType": "client_credentials"
        }
    start = timer()
    response = session.post(f'{host}/snap/v1.0/access-token/b2b', 
            headers=request_headers, 
            json=request_body
        )
    timing.append((f"Access Token: {f'{timer()-start:.3f}s'}"))
    return response


# -----------------------------------------------------------------------------
# INQUIRY
# -----------------------------------------------------------------------------
# SAMPLE_REQUEST_BODY = None
SAMPLE_REQUEST_BODY = {
    "partnerServiceId":"12345",
    "trxDateInit":"2025-03-06T14:45:00+07:00",
    "sourceBankCode":"002",
    "additionalInfo":{
        "idApp":"63bee7b6-3291-4e1c-9949-03c6e3af416b"
    },
    "passApp":"TEST",
    "customerNo":"06000009587",
    "virtualAccountNo":"1234506000009587",
    "inquiryRequestId":"5b2a065a-c9b1-410e-a23e-6736d82e00b8",
    "channelCode":1
    }
def inquiry(host: str):
    access_token_response = get_access_token(host)
    if access_token_response.status_code!=200:
        return access_token_response

    access_token = access_token_response.json()['accessToken']
    # access_token = 'asjdklajsdafjpjapljfa;ljklajfqa'
    path = '/snap/v1.0/transfer-va/inquiry'
    timestamp = datetime.now(timezone.utc).astimezone()\
                    .isoformat(timespec='milliseconds')
    if not SAMPLE_REQUEST_BODY:
        virtualAccountNo = VIRTUAL_ACCOUNT
        partnerServiceId = VIRTUAL_ACCOUNT[:5]
        customerNo = VIRTUAL_ACCOUNT[5:]
        request_body = {
            'partnerServiceId': partnerServiceId.rjust(8),
            # 'partnerServiceId': partnerServiceId,
            'virtualAccountNo': virtualAccountNo.rjust(28),
            'customerNo': customerNo,
            'inquiryRequestId': '123123123123123',
            'trxDateInit': timestamp
        }
    else:
        request_body = SAMPLE_REQUEST_BODY
        request_body.update(trxDateInit=timestamp)

    inquiry_signature = Crypto.create_signature_transactional(
            http_method='POST',
            path=path, 
            request_body=request_body, 
            timestamp=timestamp,
            access_token=access_token,
            algorithm = 'HMAC-SHA512'
        )
    request_headers = {
            'Authorization': f'Bearer {access_token}',
            # 'Authorization': f'Bearer klajsdkjalsdjaasd938423j',
            'CONTENT-TYPE': 'application/json',
            # NOTE gak mudeng artinya X-PARTNER-ID
            'X-PARTNER-ID': CLIENT_ID,
            # 'X-PARTNER-ID': 'CLIENT_ID',
            'X-TIMESTAMP': timestamp,
            'X-SIGNATURE': inquiry_signature,
            # 'X-SIGNATURE': 'aaaaaaaaaaaaaaaaaaaaa',
            # 'X-EXTERNAL-ID': 'aaaaaaaaaaaaaaaaaa',
            'X-EXTERNAL-ID': secrets.token_hex(8),
            'CHANNEL-ID': 'asdfg',
            'Cache-Control': 'no-cache'
        }
    start = timer()
    response = session.post(f'{host}{path}', 
            headers=request_headers, 
            json=request_body
        )
    # request_headers.update({'X-EXTERNAL-ID': secrets.token_hex(8)})
    # response = session.post(f'{host}{path}', 
    #         headers=request_headers, 
    #         json=request_body
    #     )
    timing.append((f"Inquiry: {f'{timer()-start:.3f}s'}"))
    return response


# -----------------------------------------------------------------------------
# PAYMENT
# -----------------------------------------------------------------------------
def payment(host: str, amount: float):
    access_token_response = get_access_token(host)
    if access_token_response.status_code!=200:
        return access_token_response

    access_token = access_token_response.json()['accessToken']
    path = '/snap/v1.0/transfer-va/payment'
    timestamp = datetime.now(timezone.utc).astimezone()\
                .isoformat(timespec='milliseconds')
    virtualAccountNo = VIRTUAL_ACCOUNT
    partnerServiceId = VIRTUAL_ACCOUNT[:5]
    customerNo = VIRTUAL_ACCOUNT[5:]
    request_body = {
        'partnerServiceId': partnerServiceId.rjust(8),
        'virtualAccountNo': virtualAccountNo.rjust(28),
        'customerNo': customerNo,
        'paymentRequestId': '123123123123123',
        'paidAmount': {'value': '{:.2f}'.format(amount), 'currency': 'IDR'},
        # 'paidAmount': {'value': str(amount), 'currency': 'IDR'}
        # 'paidAmount': {'value': amount}
        "additionalInfo": {
            "idApp": "TEST",
            "passApp": "b7aee423dc7489dfa868426e5c950c677925f3b9",
            "hashedSourceAccountName": "/bWljaGFlbCBh=="
        }
    }
    payment_signature = Crypto.create_signature_transactional(
            http_method='POST',
            path=path, 
            request_body=request_body, 
            timestamp=timestamp,
            access_token=access_token,
            algorithm = 'HMAC-SHA512'
        )
    request_headers = {
            'Authorization': f'Bearer {access_token}',
            # 'Authorization': f'Bearer klajsdkjalsdjaasd938423j',
            'CONTENT-TYPE': 'application/json',
            'X-PARTNER-ID': CLIENT_ID,
            # 'X-PARTNER-ID': 'CLIENT_ID',
            'X-TIMESTAMP': timestamp,
            'X-SIGNATURE': payment_signature,
            # 'X-SIGNATURE': 'aaaaaaaaaaaaaaaaaaaaa',
            # 'X-EXTERNAL-ID': 'aaaaaaaaaaaaaaaaaa',
            'X-EXTERNAL-ID': secrets.token_hex(8),
            'CHANNEL-ID': 'asdfg',
            'Cache-Control': 'no-cache'
        }
    start = timer()
    response = session.post(f'{host}{path}', 
            headers=request_headers, 
            json=request_body
        )
    # response = session.post(f'{host}{path}', 
    #         headers=request_headers, 
    #         json=request_body
    #     )
    timing.append((f"Payment: {f'{timer()-start:.3f}s'}"))
    return response


if __name__ == '__main__':
    parser = argparse.ArgumentParser(add_help=False)
    parser.add_argument("action", 
            nargs="?", 
            default="token", 
            help="token, inquiry, payment"
        )
    parser.add_argument("-h", "--host", 
            default='http://localhost:8000', 
            help="Hostname, default 'localhost'"
        )
    parser.add_argument("-a", "--amount", help="Payment Amount")
    args = parser.parse_args()
    host = args.host
    amount = args.amount and float(args.amount) or PAID_AMOUNT
    action = args.action
    if action == 'token':
        response = get_access_token(host)
    elif action == 'inquiry':
        response = inquiry(host)
    elif action == 'payment':
        response = payment(host, amount)
    else:
        raise ValueError('Not Implemented')

    print('Request:')
    print(to_curl(response.request))
    print('Response:')
    print('\n'.join([
            f'{k.title()}: {v}' for k, v in response.headers.items() 
        ]))
    print(json.dumps(response.json(), indent=2))
    for t in timing:
        print(t)

session.close()