{
    'name': 'OM Account Bank Statement IT',
    'version': '1.0',
    'summary': 'Backdated sequence numbering for bank statements',
    'description': '''
        This module allows custom sequence generation for Account Bank Statements
        based on the backdated accounting date, ensuring consistency and traceability
        for financial records.
        ''',
    'category': 'Accounting',
    'author': 'A Yazid Bustomi',
    'website': 'https://www.bustomi.my.id/',
    'license': 'LGPL-3',
    'depends': ['account', 'stock', 'mrp', 'purchase', 'hr', 'account_asset'],
    'data': [
    ],
    'installable': True,
    'auto_install': False
}
