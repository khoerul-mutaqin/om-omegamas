{
    'name': 'OM Inventory Location IT',
    'version': '1.0',
    'description': 'Implement Backdating for Inventory Receipts and Include Necessary Accounting Fields',
    'author': 'A Yazid Bustomi',
    'website': 'https://www.bustomi.my.id/',
    'depends': ['base','stock', 'account'],
    'data': [
        'views/inventory_location_views.xml',
    ],
    'installable': True,
    'auto_install': False
}