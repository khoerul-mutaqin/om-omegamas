
# -*- coding: utf-8 -*-
# Part of Odoo Falinwa Edition. See LICENSE file for full copyright and licensing details.
{
    'name': 'CDP OM Buku Besar Piutang, Utang, dan Rincian Valuasi Persediaan ',
    'version': '18.0.0.0.0',
    'license': 'OPL-1',
    'summary': "Falinwa",
    "category": "Tools",
    'author': "khoerul - Falinwa",
    'description': '''
    CDP OM Buku Besar Piutang, Utang, dan Rincian Valuasi Persediaan 
    ''',
    'depends': [
        'base',
        'account',
        'stock',
    ],
    "data": [
        "views/account_move_line.xml",
        "views/stock_move_views.xml",
    ],
    'images': [],
    'demo': [],
}
