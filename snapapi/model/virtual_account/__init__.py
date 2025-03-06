# -*- coding: utf-8 -*-
# SNAP-API Model Virtual Account: init
# Author: S Deta Harvianto <sdetta@gmail.com>

from typing import Final

DEFAULT_INQUIRYREASON = {'english': 'Success', 'indonesia': 'Sukses'}
DEFAULT_INQUIRYSTATUS: Final = '00'
DEFAULT_PAYMENTREASON = DEFAULT_INQUIRYREASON.copy()
DEFAULT_PAYMENTSTATUS: Final = DEFAULT_INQUIRYSTATUS