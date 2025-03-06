# -*- coding: utf-8 -*-
# SNAP-API Setting
# System wide all apps configuration
# Author: S Deta Harvianto <sdetta@gmail.com>

import os
import functools

from pathlib import Path
from configparser import ConfigParser

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

@functools.lru_cache(maxsize=128)
def build_settings(config_contents: str) -> ConfigParser:
    config = ConfigParser()
    config.read_string(config_contents)
    return config

config = build_settings(config_contents)
config_idsnap = config['snapapi']

# base setting for all apps
CACHE = config_idsnap.get('cache')

# detik, Token Expires SNAP 15 menit, 1 detik sebagai overhead
TOKEN_EXPIRE = int(config_idsnap.get('token_expire', 60*15 - 1))
# detik, Timeout SNAP 10 detik, 1 detik sebagai overhead
TIMEOUT = int(config_idsnap.get('timeout', 9))

# Memcacahed
MEMCACHED_HOST = config_idsnap.get('memcached_host', 'localhost')
MEMCACHED_PORT = int(config_idsnap.get('memcached_port', 11211))

# Redis
REDIS_HOST = config_idsnap.get('redis_host', 'localhost')
REDIS_PORT = int(config_idsnap.get('redis_port', 6379))
REDIS_DB = int(config_idsnap.get('redis_db', 8))