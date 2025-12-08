{
    'name': 'Custom Employee Type',
    'version': '1.0',
    'depends': ['base','hr'],
    'data': [
        'security/ir.model.access.csv',
        'views/hr_employee.xml',
        'views/surat_peringatan_views.xml',
        'views/hr_employee_menu.xml',
        'views/export_sp_wizard_view.xml',
    ],
    'installable': True,
    'auto_install': False,
}
