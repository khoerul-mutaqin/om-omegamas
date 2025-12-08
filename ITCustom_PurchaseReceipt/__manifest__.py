{
    'name': 'IT Custom Purchase Receipt',
    'version': '1.0',
    'summary': 'Custom module to add products in receipts with a custom wizard',
    'description': '''
        This module provides a custom wizard to add products directly in inventory receipts,
        different from adding products from purchase orders.
    ''',
    'author': 'A Yazid Bustomi',
    'website': 'https://www.bustomi.my.id/',
    'license': 'LGPL-3',
    'depends': ['stock', 'purchase', 'account', 'analytic'],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_picking_views.xml',
        'wizard/add_products_wizard_views.xml',
    ],
    'installable': True,
    'auto_install': False,
}
