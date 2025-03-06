# -*- coding: utf-8 -*-
# SNAP-API App Demo: Main
# Author: S Deta Harvianto <sdetta@gmail.com>

from snapapi.cache import SNAPCache
from snapapi.security.crypto import SNAPCrypto

from app.setting import (
        config, 
        CONFIG_PATH, 
        TIMEOUT,
        CACHE,
        MEMCACHED_HOST, MEMCACHED_PORT,
        REDIS_HOST, REDIS_PORT, REDIS_DB
    )

config_demo = config['demo']
NAMESPACE = config_demo['namespace']
FLOW = 'inbound'
CLIENT_ID = config_demo['client_id']
CLIENT_SECRET = config_demo['client_secret']
TOKEN_PASSPHRASE = config_demo['token_passphrase']

# Hanya Flow API -> Bank yang punya Private Key
try:
    private_key_file = CONFIG_PATH / f'{NAMESPACE}.key.pem'
    with open(private_key_file, 'rb') as private_key:
        PRIVATE_KEY = private_key.read()
    if oct(private_key_file.stat().st_mode)[-3:] != '600':
        raise SystemError(f"{private_key_file} permission harus diset 600")
except FileNotFoundError:
    PRIVATE_KEY = b''

# Apapun flownya, Public Cert harusnya selalu ada
try:
    public_cert_file = CONFIG_PATH / f'{NAMESPACE}.cert.pem'
    with open(public_cert_file, 'rb') as public_cert:
        PUBLIC_CERT = public_cert.read()
    if oct(public_cert_file.stat().st_mode)[-3:] != '600':
        raise SystemError(f"{public_cert_file} permission harus diset 600")
except FileNotFoundError:
    PUBLIC_CERT = b''


# Di-instantiate sekali saat loading
HOST = PORT = DB = None
if CACHE == 'redis':
    HOST = REDIS_HOST
    PORT = REDIS_PORT
    DB = REDIS_DB
elif CACHE == 'memcached':
    HOST = MEMCACHED_HOST
    PORT = MEMCACHED_PORT
Cache = SNAPCache(NAMESPACE,
            backend=CACHE,
            host=HOST,
            port=PORT,
            db=DB,
            timeout=TIMEOUT
        )

Crypto = SNAPCrypto(
        client_id = CLIENT_ID,
        client_secret = CLIENT_SECRET,
        public_cert = PUBLIC_CERT,
        token_passphrase = TOKEN_PASSPHRASE
    )