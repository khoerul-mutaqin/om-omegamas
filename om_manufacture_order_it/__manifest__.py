{
    'name': 'OM Manufacturing Order IT',
    'version': '1.0',
    'summary': 'Backdate Manufacturing Journal Entries and Add Confirmation Wizard',
    'description': '''
        This module extends the Manufacturing Order functionality by:
        - Enabling backdating of journal entries related to manufacturing operations
        - Adding custom confirmation wizards for production actions
        ''',
    'category': 'Manufacturing',
    'author': 'A Yazid Bustomi',
    'website': 'https://www.bustomi.my.id/',
    'license': 'LGPL-3',
    'depends': ['mrp', 'account'],
    "data": [
        'security/ir.model.access.csv',
        'views/mrp_production_list_views.xml',
        'wizard/confirm_action_wizard_views.xml',
        'wizard/confirm_mark_done_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
}
