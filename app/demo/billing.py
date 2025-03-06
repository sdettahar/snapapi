# -*- coding: utf-8 -*-
# SNAP-API App Demo: Billing
# Author: S Deta Harvianto <sdetta@gmail.com>

import re
from typing import List
from snapapi.exceptions import (
        BillNotFound,
        BillInvalidAmount,
        BillPaid,
        BillExpired,
        VirtualAccountNotFound
    )

DATA = [
    # Inquiry dan Payment
    {
        'account': '1234506000009587',
        'accountName': 'Matt Murdock',
        'totalAmount': 103500.0,
        'billDetails': [{
            'billNo': 'INV/2025/00123456',
            'billDescription': {
                'english': 'Torch, Flashlight',
                'indonesia': 'Lampu Senter'
            },
            'billAmount': 103500.0,
            'billStatus': 'unpaid'
        }]
    },
    # Contoh Paid Bill bahasa Indonesia
    {
        'account': '1234505000001234',
        'accountName': 'Karen Page',
        'totalAmount': 0.0,
        'billDetails': [{
            'billNo': 'INV/2025/00123457',
            'billDescription': {
                'english': 'Tape recorder',
                'indonesia': 'Tape recorder'
            },
            'billAmount': 208000.0,
            'billStatus': 'paid'
        }]
    },
    # Contoh Expired Bill
    {
        'account': '1234505000005678',
        'accountName': 'Frank Castle',
        'totalAmount': 0.0,
        'billDetails': [{
            'billNo': 'INV/2025/00123458',
            'billDescription': {
                'english': '2 lbs Chimichanga',
                'indonesia': '1 kg Chimichanga'
            },
            'billAmount': 300000.0,
            'billStatus': 'expired'
        }]
    },      
    # Contoh No Bill (tidak ada Tagihan)
    {
        'account': '1234505000008984',
        'accountName': 'Elektra',
        'totalAmount': 0.0,
        'billDetails': []
    },
]

class BillDemo:
    def __init__(
            self,
            service_code: str
        ) -> None:
        assert service_code, 'service_code mandatory'
        self.service_code = service_code

    async def inquiry(self, account: str) -> dict:
        result = list(filter(lambda b: b and b['account'] == account, DATA))
        bill: dict = await self._check(bill=result and result[0] or {})
        return await self._parse_to_snap(bill)

    async def payment(self, account: str, payment_amount: float) -> dict:
        result = list(filter(lambda b: b and b['account'] == account, DATA))
        bill = await self._check(bill=result and result[0] or {})
        # DEMO: Closed Bill only
        if payment_amount != bill['totalAmount']:
            raise BillInvalidAmount()
        return await self._parse_to_snap(bill)

    async def _check(self, bill: dict) -> dict:
        if not bill:
            raise VirtualAccountNotFound()
        if not bill.get('billDetails'):
            raise BillNotFound()
        # DEMO: Single Bill only
        bill_status = list(map(lambda b: 
                b['billStatus'], bill['billDetails']
            ))[0]
        if bill_status == 'paid':
            raise BillPaid()
        if bill_status == 'expired':
            raise BillExpired()
        return bill

    async def _parse_to_snap(self, bill: dict) -> dict:
        """ Parsing Bill sesuai dengan model BillBackend """
        totalAmount = dict(value='{:.2f}'.format(bill['totalAmount']),
                        currency='IDR')
        billDetails = []
        billNo = 1
        for detail in bill['billDetails']:
            billDetails.append(dict(
                    billCode=str(billNo).zfill(2),
                    # FIXME: Nomor Tagihan biasanya gak cuma angka
                    # tapi di dokumen SNAP dikasih contoh begitu
                    billNo=''.join(re.findall(r'\d+', 
                        detail.get('billNo'))),
                    billName=detail.get('billName') \
                        or f"Bill for {bill['accountName']}"[:20],
                    billDescription=detail['billDescription'],
                    billAmount=dict(
                        value='{:.2f}'.format(detail['billAmount']),
                        currency='IDR'
                    )
                ))
            billNo += 1
        return dict(
                account=bill['account'],
                accountName=bill['accountName'],
                totalAmount=totalAmount,
                billDetails=billDetails
            )