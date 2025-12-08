{
    'name': 'Custom Time Off Employee Type',
    'version': '1.0',
    'category': 'Human Resources',
    'summary': 'Menampilkan employee_type di form time off',
    'depends': ['hr_holidays', 'hr'],
    'data': [
        'views/hr_leave_views.xml',
    ],
    'installable': True,
    'application': False,
}
