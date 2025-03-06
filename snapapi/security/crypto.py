# -*- coding: utf-8 -*-
# SNAP-API: Crpto
# Author: S Deta Harvianto <sdetta@gmail.com>

import hashlib
import _hashlib
import jwt
import hmac
import json
import base64

from typing import Union, TypeVar, Optional, Literal, Any
from datetime import datetime, timedelta, timezone

from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256
from Crypto.Signature import pkcs1_15

from snapapi import tools
from snapapi.exceptions import (
        AccessDenied,
        InvalidSignature,
        AccessTokenNotFound,
        AccessTokenInvalid
    )

AppType = TypeVar("AppType", bound="SNAPCrypto")
ALGORITHM = Literal['SHA256withRSA', 'HMAC-SHA512']


class SNAPCrypto:
    """
    class yang digunakan untuk dua jenis Flow; ke Bank/PG atau sebaliknya.

    Flow: API ---> Bank/Payment Gateway
    -----------------------------------
    Instantiate
        ```python

        Crypto = SNAPCrypto(
                client_id = CLIENT_ID,
                client_secret = CLIENT_SECRET,
                private_key = PRIVATE_KEY
            )

        ```
    1. Membuat OAuth2 Signature untuk mendapatkan Access Token dari Bank/PG.

       ```python
       
        string_to_sign = f"{CLIENT_ID}|{timestamp}".encode()
        oauth2_signature = Crypto.create_signature_oauth2(
                string_to_sign,
                algorithm = 'SHA256withRSA'
            )

        response = requests.post('https://localhost')

        ```

    2. Membuat Transactional Signature.

       ```python
       
       transactional_signature = Crypto.create_signature_transactional(
                http_method = 'POST',
                path = '/snap/v1.0/transfer-va/inquiry',
                timestamp = '2025-01-03T14:06:47.798+07:00',
                request_body = request_body_dict,
                access_token = access_token,
                algorithm = 'HMAC-SHA512'
            )

        ```

    Flow: Bank/Payment Gateway ---> API
    -----------------------------------
    Instantiate

        ```python
       
       Crypto = SNAPCrypto(
                client_id = CLIENT_ID,
                client_secret = CLIENT_SECRET,
                public_cert = PUBLIC_CERT,
                token_passphrase = TOKEN_PASSPHRASE
            )

        ```

    1. Access Token untuk Partner       
        a. Membuat Access Token untuk Partner.
            ```python
            
            access_token = Crypto.create_access_token(
                    request_headers = request_headers_dict,
                    signature_algorithm = 'SHA256withRSA'
                )

            ```
        
        b. Memverifikasi Acccess Token dari Partner.
           Jika invalid/not found maka akan 
           raise AccessTokenInvalid atau AccessTokenNotFound.
            
            ```python
            
            Crypto.verify_access_token(access_token)

            ```
    
    2. Memverifikasi Transactional Signature dari Partner

        ```python

        Crypto.verify_signature_transactional(
                path = '/snap/v1.0/transfer-va/inquiry',
                http_method = 'POST',
                access_token = access_token,
                request_headers = request_headers_dict,
                request_body = request_body_dict
            )

        ```

    """
    def __init__(
            self: AppType, 
            *,
            private_key: Union[bytes, str, None] = None,
            private_key_passphrase: Optional[str] = None,
            public_cert: Union[bytes, str, None] = None,
            client_id: Union[str, None] = None,
            client_secret: Union[bytes, str, None] = None,
            token_passphrase: Union[bytes, str, None] = None
        ):
        self._client_id = client_id
        self._client_secret = client_secret
        self._private_key = private_key
        self._private_key_passphrase = private_key_passphrase
        self._public_cert = public_cert
        self._token_passphrase = token_passphrase
        self._key = self.initiate_key()

    @property
    def client_id(self) -> str:
        """ :type: str """
        if not self._client_id:
            return ''
        client_id = self._client_id
        if not isinstance(client_id, str):
            client_id = client_id.decode()
        return client_id

    @property
    def client_secret(self) -> bytes:
        """ :type: bytes """
        if not self._client_secret:
            return b''
        client_secret = self._client_secret
        if not isinstance(client_secret, bytes):
            client_secret = client_secret.encode()
        return client_secret

    @property
    def token_passphrase(self) -> bytes:
        """ :type: bytes """
        if not self._token_passphrase:
            return b''
        token_passphrase = self._token_passphrase
        if isinstance(token_passphrase, str):
            token_passphrase = token_passphrase.encode()
        return token_passphrase

    @property
    def private_key(self) -> bytes:
        """ :type: bytes """
        return isinstance(self._private_key, str)\
            and self._private_key.encode() or b''

    @private_key.setter
    def private_key(self, private_key: Union[bytes, str, None]) -> None:
        if isinstance(private_key, str):
            private_key = private_key.encode()
        self._private_key = private_key
        self.initiate_key()
    
    @property
    def public_cert(self) -> bytes:
        """ :type: bytes """
        return isinstance(self._public_cert, str)\
            and self._public_cert.encode() or b''

    @public_cert.setter
    def public_cert(self, public_cert: Union[bytes, str, None]) -> None:
        if isinstance(public_cert, str):
            public_cert = public_cert.encode()
        self._public_cert = public_cert
        self.initiate_key()

    @property
    def key(self) -> Union[RSA.RsaKey, None]:
        """ 
        Readonly. Hanya berubah jika _private_key / _public_cert berubah
        """
        return self._key

    def initiate_key(self) -> Union[RSA.RsaKey, None]:
        if self._private_key != None:
            key = RSA.importKey(
                    self._private_key, 
                    self._private_key_passphrase
                )
        elif self._public_cert:
            key = RSA.importKey(self._public_cert)
        else:
            key = None
        self._key = key
        return key

    def __str__(self)->str:
        return f"client_id='{self._client_id}', "\
            f"key='{self.key}'"

    def __repr__(self)->str:
        return f"{self.__class__.__name__}({self.__str__()})"

    def encode_string_to_sign(
            self,
            *,
            path: str,
            timestamp: str,
            request_body: dict,
            http_method: str,
            access_token: Union[str, None] = None
        ) -> bytes:
        """ 
        Format string_to_sign untuk Transactional Signature:

            With AccessToken (BRI, BCA, Mandiri):
                HTTPMethod 
                + ”:“ 
                + Path
                + ":" 
                + AccessToken 
                + ":“ 
                + Lowercase(HexEncode(SHA-256(minify(RequestBody))))
                + ":“ 
                + TimeStamp

            Without AccessToken (DANA):
                HTTPMethod 
                + ”:“
                + Path
                + ":" 
                + Lowercase(HexEncode(SHA-256(minify(RequestBody)))) 
                + ":“ 
                + TimeStamp

        """
        request_body_mini: str = ''
        request_body_hashed: _hashlib.HASH
        request_body_digest: str
        digest_message: bytes

        assert http_method, 'http_method mandatory'
        if not isinstance(request_body, dict):
            raise TypeError('headers harus dict')
        if request_body:
            request_body_mini = json.dumps(request_body, separators=(',',':'))
        
        http_method = http_method.upper()
        timestamp = tools.datetime_string(timestamp)
        request_body_hashed = hashlib.sha256(request_body_mini.encode())
        request_body_digest = request_body_hashed.hexdigest().lower()
        if access_token:
            digest_message = f"{http_method}:{path}:{access_token}:"\
                             f"{request_body_digest}:{timestamp}".encode()
        else:
            digest_message = f"{http_method}:{path}:"\
                             f":{request_body_digest}:{timestamp}".encode()
        return digest_message

    def create_signature(
                self,
                string_to_sign: bytes,
                *,
                algorithm: ALGORITHM
        ) -> str:
        """ 
        Create Signature either w/ algo: 'SHA256withRSA' or 'HMAC-SHA512'.

        Untuk OAuth2 Signature, bentuk string_to_sign adalah:
            
            CLIENT_ID|TIMESTAMP
        
        dimana:
        - **CLIENT_ID** : Client ID dari Bank
        - **|**         : delimiter '|'
        - **TIMESTAMP** : Timestamp ISO 8601, 
                          format: '2021-11-29T09:22:18.172+07:00'

        Sedangkan untuk Transactional Signature lihat `encode_string_to_sign`.
        """
        assert string_to_sign, 'string_to_sign mandatory'
        signature: bytes = algorithm == 'SHA256withRSA'\
            and self._create_signature_SHA256withRSA(string_to_sign)\
            or self._create_signature_HMAC_SHA512(string_to_sign)
        return signature.decode()

    def _create_signature_SHA256withRSA(self, string_to_sign: bytes) -> bytes:
        """ Signature untuk OAuth2 """
        assert self.key, 'private_key is required'
        sha256_hash: SHA256.SHA256Hash = SHA256.new(string_to_sign)
        scheme: pkcs1_15.PKCS115_SigScheme = pkcs1_15.new(self.key)
        signature: bytes = scheme.sign(sha256_hash)
        return base64.b64encode(signature)

    def _create_signature_HMAC_SHA512(self, string_to_sign: bytes) -> bytes:
        """ Signature untuk Transactional """
        hmac_digest: bytes = hmac.digest(
                                    self.client_secret,
                                    string_to_sign,
                                    hashlib.sha512
                                )
        return base64.b64encode(hmac_digest)


    def create_signature_oauth2(
            self, 
            string_to_sign: bytes,
            *,
            algorithm: ALGORITHM = 'SHA256withRSA'
        ) -> str:
        """ Just alias to `create_signature` """
        return self.create_signature(string_to_sign, algorithm=algorithm)

    def create_signature_transactional(
            self,
            *,
            path: str,
            timestamp: str,
            request_body: dict,
            http_method: str,
            algorithm: ALGORITHM = 'HMAC-SHA512',
            access_token: Union[str, None] = None
        ) -> str:
        """ 
        Verifikasi OAuth2 Signature

        Raises:
        - `AssertionError`: programmer error
        - `InvalidSignature`: X-Signature Invalid -> CASE_CODE_00
        """
        digest_string = self.encode_string_to_sign(
                path=path,
                timestamp=timestamp,
                request_body=request_body,
                http_method=http_method,
                access_token=access_token
            )
        return self.create_signature(digest_string, algorithm=algorithm)

    def verify_signature_transactional(
            self,
            *,
            path: str,
            access_token: str,
            request_headers: dict,
            request_body: dict,
            algorithm: ALGORITHM = 'HMAC-SHA512',
            http_method: str = 'POST',
            payload_key: Union[str, None] = None
        ) -> None:
        """ 
        Verifikasi Transactional Signature

        Returns `None`
        Raises:
        - `AssertionError`: programmer error
        - `InvalidSignature`: X-Signature Invalid -> CASE_CODE_00

        Note: 
        Adakalanya string-to-sign yang digunakan untuk membuat Signature 
        berbeda cara atau method encodenya. Misal, diencode dengan encoding
        selain 'utf-8', string ada end character `\0` atau hal lain sebagainya.

        Jika itu terjadi, mungkin pihak yang membuat Signature mencantumkan 
        payload string-to-sign di dalam header.

        Nah, param 'payload_key' digunakan untuk workaround ini, diisi
        dengan key headers yang berisi string-to-sign oleh requestor.
        """
        assert path, 'path mandatory'
        assert request_headers, 'request_headers mandatory'
        assert isinstance(request_headers, dict), 'request_headers harus dict'
        assert request_body, 'request_body mandatory'
        assert isinstance(request_body, dict), 'request_body harus dict'
        assert access_token, 'access_token mandatory'

        # note: pydantic convert 'x-signature' jadi 'x_signature'
        request_headers = tools.parse_headers(request_headers)
        digest_string = self.encode_string_to_sign(
                path=path,
                timestamp=request_headers['x-timestamp'],
                request_body=request_body,
                http_method=http_method,
                access_token=access_token
            )
        try:
            return self.verify_signature(
                    message=digest_string,
                    signature=request_headers['x-signature'].encode(),
                    algorithm=algorithm
                )
        except Exception as exc:
            if not payload_key:
                # nothing to do .. move along ..
                raise exc
            # workaround
            try:
                digest_string = request_headers['payload_key'].encode()
                return self.verify_signature(
                        message=digest_string,
                        signature=request_headers['x-signature'].encode(),
                        algorithm=algorithm
                    )
            except:
                # re-raise original Exception
                raise exc

    def verify_signature(
            self,
            *,
            message: bytes,
            signature: bytes,
            algorithm: ALGORITHM
        ) -> None:
        """ 
        Verify Signature either 'SHA256withRSA' or 'HMAC-SHA512'
        Digunakan untuk OAuth2 dan Transactional request

        Returns `None`
        Raises:
        - `AssertionError`: programmer error
        - `InvalidSignature`: X-Signature Invalid
        """
        assert message and signature, 'message and signature are mandatory'
        if algorithm == 'SHA256withRSA':
            self._verify_signature_SHA256withRSA(message, signature)
        else:
            self._verify_signature_HMAC_SHA512(message, signature)
        return None

    def _verify_signature_SHA256withRSA(
            self,
            message: bytes, 
            signature: bytes
        ) -> None:
        """ Private verifikasi signature algo SHA256withRSA """
        assert self.key, 'public_cert is required'
        try:
            sha256_hash: SHA256.SHA256Hash = SHA256.new(message)
            scheme: pkcs1_15.PKCS115_SigScheme = pkcs1_15.new(self.key)
            scheme.verify(sha256_hash, base64.b64decode(signature))
            return None
        except ValueError as exc:
            raise InvalidSignature()

    def _verify_signature_HMAC_SHA512(
            self,
            message: bytes, 
            signature: bytes
        ) -> None:
        """ Private verifikasi signature algo HMAC-SHA512 """
        valid_signature: bytes
        valid_signature_digest: bytes
        signature_digest: bytes
        valid_signature = self._create_signature_HMAC_SHA512(message)
        valid_signature_digest = base64.b64decode(valid_signature)
        try:
            signature_digest = base64.b64decode(signature)
            assert hmac.compare_digest(
                    valid_signature_digest, 
                    signature_digest
                )
        except:
            raise InvalidSignature()
        return None

    def create_access_token(
            self,
            *,
            request_headers: dict,
            signature_algorithm: ALGORITHM = 'SHA256withRSA',
            expires_in: int = 899
        ) -> str:
        """ 
        Create Access Token dengan menggunakan JWT.
        
        Note: 
        token_passphrase yang digunakan HARUS BERBEDA dengan client_secret

        Silakan generate token_passphrase, contoh:

            ```python
            
            import secrets
            secrets.token_urlsafe(32)
            
            ```

        Raises:
        - AssertionError: programmer error
        - AccessDenied: Client ID != X-Partner-ID
        - InvalidSignature: X-Signature Invalid -> CASE_CODE_00
        """
        assert signature_algorithm, 'signature_algorithm mandatory'
        assert request_headers, 'request_headers mandatory'
        assert self.token_passphrase, 'token_passphrase mandatory'
        assert self.client_id, 'client_id mandatory'
        assert self.client_secret, 'client_secret mandatory'
        # sering saat buat jwt, pakai client_secret
        assert not hmac.compare_digest(
                self.client_secret, 
                self.token_passphrase
            ), 'client_secret tidak boleh sama dengan token_passphrase'
        # note: pydantic convert 'x-signature' jadi 'x_signature'
        request_headers = tools.parse_headers(request_headers)
        if not self.client_id == request_headers['x-client-key']:
            raise AccessDenied()

        message=f"{self.client_id}|{request_headers['x-timestamp']}"
        self.verify_signature(
                message=message.encode(),
                signature=request_headers['x-signature'].encode(),
                algorithm=signature_algorithm
            )
        iat: datetime = datetime.now(timezone.utc)
        exp: datetime = iat + timedelta(seconds=expires_in)
        payload = {
                'iat': iat,
                'exp': exp
            }
        return jwt.encode(payload, self.token_passphrase, algorithm='HS512')

    def verify_access_token(
            self,
            access_token: str,
            /
        ) -> None:
        """ 
        Verify JWT access_token

        Raises:
        - AccessTokenInvalid: Access Token Invalid -> CASE_CODE_01
        - AccessTokenNotFound: Access Token Not Found -> CASE_CODE_03
        """
        try:
            assert access_token
            _ = jwt.decode(access_token, self.token_passphrase, 
                algorithms=['HS512'])
        except AssertionError:
            raise AccessTokenNotFound()
        except Exception as exc:
            raise AccessTokenInvalid()
        return None