{
    'name': 'Appraisal Template',
    'version': '1.0',
    'depends': ['hr_appraisal', 'hr_appraisal_skills'],
    'category': 'Human Resources',
    'summary': 'Manage Templates for Appraisal',
    'description': 'Add configuration menu for appraisal templates and extend hr.appraisal with Skills tab enhancements',
    'data': [
        'security/security.xml',
        'security/ir.model.access.csv',
        'views/appraisal_template_views.xml',
        'views/performance_guidelines_views.xml',
        'views/performance_guidelines_wizard_views.xml',
        'views/hr_appraisal_skills_inherit.xml',
        'views/hr_skill_type_inherit.xml',
        'views/hr_appraisal_inherit.xml',
        'views/hr_appraisal_skill_inherit.xml',
    ],
    'assets': {
        'web.assets_backend': [
        ],
    },
    'installable': True,
    'application': False,
}
