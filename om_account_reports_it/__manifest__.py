{
    'name': 'OM Account Reports IT',
    'version': '1.0',
    'summary': 'Enhance account reports with total amount currency and bank statement integration',
    'description': '''
        This module enhances the accounting reports by:
        - Adding support for displaying Total Amount in Currency
        - Integrating bank statement data into relevant financial reports
        ''',
    'category': 'Accounting',
    'author': 'A Yazid Bustomi',
    'website': 'https://www.bustomi.my.id/',
    'license': 'LGPL-3',
    'depends': ['account', 'stock', 'mrp', 'purchase', 'hr', 'om_purchase_order_it', 'om_inventory_receipts_it'],
    'installable': True,
    'auto_install': False
}
