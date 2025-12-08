# File: __manifest__.py
{
    'name': 'Custom Attendance Report',
    'version': '1.0',
    'depends': ['hr_payroll', 'hr', 'hr_contract'],
    'author': 'Taufiqur Rahman',
    'category': 'Payroll',
    'summary': 'Menambahkan menu All Report di Attendance',
    'data': [
        'views/hr_payroll.xml',
        'views/hr_salary_attachment.xml',
        'views/hr_contract.xml',
        # 'views/hr_payslip_views.xml',
        'views/hr_payslip_check_action.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'ITCustom_Payroll/static/src/css/custom_style.css',
        ],
    },
    'installable': True,
    'application': False,
}
