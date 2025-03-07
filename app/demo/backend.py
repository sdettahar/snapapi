# -*- coding: utf-8 -*-
# SNAP-API Demo: Backend
# Author: S Deta Harvianto <sdetta@gmail.com>

from typing import Dict, Any
from pprint import pformat as pp


async def logger(log: Dict[str, Any]) -> None:
    """ sender kan be anything; HTTP Client, RPC, Celery Task, etc """
    try:
        # send here
        print('This is Logger\n: ', pp(log))
        pass
    except:
        # never raise Exception
        # Tips: Celery lebih cocok untuk tugas ini, karena Exception
        # akan dikelola oleh Celery; misal retries management dll
        pass