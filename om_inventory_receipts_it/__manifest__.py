{
    'name': 'OM Inventory Receipts IT',
    'version': '1.0',
    'summary': 'Backdate Inventory Receipts and Add Sales Order Lines',
    'description': '''
            This module provides the following features for inventory receipts:
            - Enable backdating functionality for inventory operations.
            - Add necessary accounting and analytic fields.
            - Add a button to import Sales Order lines into inventory receipts.
            ''',
    'author': 'A Yazid Bustomi',
    'website': 'https://www.bustomi.my.id/',
    'license': 'LGPL-3',
    'depends': ['stock', 'om_purchase_order_it', 'om_purchase_manual_delivery', 'account', 'purchase', 'analytic', 'om_sale_it'],
    "data": [
        "security/ir.model.access.csv",
        "views/stock_move_line_views.xml",
        "views/stock_picking_list_views.xml",
        "wizard/add_so_products_wizard_views.xml",
        "views/stock_picking_views.xml",
    ],
    'installable': True,
    'auto_install': False
}
