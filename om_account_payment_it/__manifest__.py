{
    'name': 'OM Account Payment Bill IT',
    'version': '1.0',
    'summary': 'Custom payment sequence based on bank code and payment date with last payment tracking',
    'description': '''
                    This module customizes the payment numbering sequence based on the bank code and payment date.
                    It also displays the most recent payment made for easier tracking and reconciliation.
                    ''',
    'category': 'Accounting',
    'author': 'A Yazid Bustomi',
    'license': 'LGPL-3',
    'website': 'https://www.bustomi.my.id/',
    'depends': ['account', 'stock', 'mrp', 'purchase'],
    'data': [
        'views/account_move_tree_inherit_views.xml'
    ],
    'installable': True,
    'auto_install': False
}
