
# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "OM Add Views",
    "summary": "",
    "version": "18.0",
    "category": "",
    "website": "",
    "author": "Azhar Zulkifli N",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ['purchase','sale','account','sale_blanket_order','stock'],
    "data": [
        'views/account.xml',
        'views/purchase.xml',
        'views/stock.xml',
    ],
}
