{
    'name': 'OM Accounting Stock Report IT',
    'version': '1.0',
    'summary': 'Stock Movement and Value Report IT',
    'description': '''
        Generate detailed stock movement and value reports with:
        * Opening balance and value
        * Incoming/Outgoing quantities and values
        * UoM and unit prices
        * Filterable by date range, product, and category
        * Grouping by category
    ''',
    'category': 'Accounting',
    'author': 'A Yazid Bustomi',
    'website': 'https://www.bustomi.my.id/',
    'depends': [
        'account',
        'stock',
        'mrp',
        'product',
        'purchase',
        'hr',
        'om_purchase_order_it',
        'om_inventory_receipts_it'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/stock_report_tree_view.xml',
        'wizard/stock_report_wizard_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': False,
    'sequence': 1,
    'license': 'LGPL-3',
}
