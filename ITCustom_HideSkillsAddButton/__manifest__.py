# -*- coding: utf-8 -*-
{
    'name': 'IT Custom Hide Skills Add Button',
    'version': '18.0.1.0.0',
    'category': 'Human Resources',
    'summary': 'Hide ADD button in skills one2many field',
    'description': """
        This module hides the ADD button in the skills one2many field
        to prevent users from adding new skills directly from the form view.
    """,
    'author': 'IT Custom',
    'depends': ['hr_skills'],
    'data': [],
    'assets': {
        'web.assets_backend': [
            'ITCustom_HideSkillsAddButton/static/src/scss/hide_skills_add_button.scss',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
