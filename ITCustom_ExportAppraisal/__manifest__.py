# -*- coding: utf-8 -*-
{
    'name': 'IT Custom Print Appraisal',
    'version': '1.0',
    'summary': 'Tambahkan tombol Print pada hr.appraisal',
    'description': 'Module untuk menambahkan tombol Print bawaan Odoo di hr.appraisal',
    'author': 'IT Team',
    'category': 'Human Resources',
    'depends': ['hr_appraisal', 'base'],
    'data': [
        'views/hr_appraisal_views.xml',
        'reports/hr_appraisal_action.xml',
        'reports/hr_appraisal_template.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
