# -*- coding: utf-8 -*-
# SNAP-API: Tools
# Author: S Deta Harvianto <sdetta@gmail.com>

from typing import Dict
from datetime import datetime

def parse_headers(headers: Dict[str, str]) -> Dict[str, str]:
    """ pydantic convert 'x-signature' jadi 'x_signature' """
    return {
            k.lower().replace('_', '-'): v 
            for k, v in headers.copy().items()
        }


def datetime_string(value: str) -> str:
    try:
        datetime.fromisoformat(value)
    except:
        raise ValueError("Invalid datetime_string format. "
                "Contoh: '2021-11-29T09:22:18.172+07:00'"
            )
    return value