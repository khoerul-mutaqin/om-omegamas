# -*- coding: utf-8 -*-
{
    'name': 'ITCustom Project Portal',
    'version': '1.0',
    'category': 'Project',
    'summary': 'Allow portal users to be assigned to project tasks',
    'description': """
        This module extends the default Odoo project functionality to allow portal users
        to be assigned to tasks, in addition to internal users.
    """,
    'author': 'ITCustom',
    'website': '',
    'depends': ['project', 'portal'],
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
