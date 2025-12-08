{
    'name': 'OM Accounting Journal IT',
    'version': '1.0',
    'summary': 'Adds Department and Analytic fields to Journal Items, supports custom journal sequences and backdating',
    'description': 'This module adds Department and Analytic fields to Journal Items, enables custom journal numbering format based on journal type and date, and allows backdating of journal entries',
    'category': 'Accounting',
    'author': 'A Yazid Bustomi',
    'license': 'LGPL-3',
    'website': 'https://www.bustomi.my.id/',
    'depends': ['account', 'stock', 'mrp', 'purchase', 'hr', 'om_purchase_order_it', 'om_inventory_receipts_it'],
    'data': [
        'views/account_move_line_views.xml'
    ],
    'installable': True,
    'auto_install': False
}
