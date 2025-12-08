{
    'name': 'Custom Purchase Request',
    'version': '1.0',
    'category': 'Purchases',
    'summary': 'Set default name to "Draft" when creating Purchase Request',
    'author': 'Taufiqur Rahman',
    'depends': ['om_purchase_request'],
    'data': [
        'views/purchase_request_view.xml',
    ],
    'installable': True,
    'application': False,
}
