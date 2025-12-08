# -*- coding: utf-8 -*-
{
    'name': "alugara_account",

    'summary': "Short (1 phrase/line) summary of the module's purpose",

    'description': """
Long description of module's purpose
    """,

    'author': "My Company",
    'website': "https://www.yourcompany.com",

    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    'category': 'Accounting',
    'version': '0.1',

    # any module necessary for this one to work correctly
    'depends': ['account', 'account_reports'],

    # always loaded
    'data': [
        # 'security/ir.model.access.csv',
        'data/general_ledger.xml',
        'views/account.xml',
        'views/templates.xml',
        'views/report_invoice.xml',
        'wizard/account.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
        'demo/demo.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'om_account/static/src/components/**/*',
            # 'om_account/static/src/**/*.xml',
        ]
    },
}

