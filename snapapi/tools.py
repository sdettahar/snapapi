# -*- coding: utf-8 -*-
# SNAP-API: Tools
# Author: S Deta Harvianto <sdetta@gmail.com>

from typing import Dict
from datetime import datetime, timedelta

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


async def count_second_left()->int:
    """ 
    Hitung detik yang tersisa hari ini, sesuai dengan timezone local
    """
    now: datetime = datetime.now()
    midnight: datetime = (now + timedelta(days=1)).replace(
                                hour=0, 
                                minute=0, 
                                second=0, 
                                microsecond=0
                            )
    return (midnight - now).seconds