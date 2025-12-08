{
    'name': 'Custom Payroll',
    'version': '1.0',
    'summary': 'Modul kustom untuk ekspor payroll ke format Mandiri',
    'category': 'Human Resources',
    'author': 'Name',
    'depends': ['hr_payroll'],
    'data': [
        'security/ir.model.access.csv',
        'views/custom_payroll_views.xml',
        'views/hr_payslip_wizard_views.xml',
    ],
    'installable': True,
    'application': False,
}
