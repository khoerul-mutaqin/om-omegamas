{
    'name': 'OM Inventory Reporting IT',
    'version': '1.0',
    'summary': 'Enhance Inventory Reporting with Additional Fields',
    'description': '''
        This module enhances inventory reporting by:
        - Adding additional fields to the Stock Move Line list view
        - Extending the Stock Valuation Layer view to include custom information
        ''',
    'author': 'A Yazid Bustomi',
    'website': 'https://www.bustomi.my.id/',
    'license': 'LGPL-3',
    'depends': ['stock', 'account', 'purchase', 'analytic', 'mrp', 'om_inventory_receipts_it'],
    "data": [
        "views/stock_valuation_layer_views.xml",
        "views/stock_move_line_list_views.xml",
    ],
    'installable': True,
    'auto_install': False
}
