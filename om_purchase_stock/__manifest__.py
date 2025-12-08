# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    "name": "OM Purchase Stock",
    "summary": "",
    "version": "18.0.1.0.0",
    "category": "",
    "website": "",
    "author": "Nifil A",
    "license": "AGPL-3",
    "application": False,
    "installable": True,
    "depends": ['purchase_stock', 'stock_account'],
    "data": [
        "views/stock_quant.xml",
        "views/res_config_view.xml",
        "views/stock_move.xml",
        # "views/product_product.xml",
    ],
}
