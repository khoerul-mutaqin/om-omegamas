{
    'name': 'ITCustom Footer',
    'version': '1.0',
    'depends': ['web'],
    'category': 'Customization',
    'summary': 'Add footer with print datetime to all PDF reports',
    'description': 'This module adds a footer containing the print date and time to every PDF report in Odoo.',
    'data': [
        'views/report_layout_inherit.xml',
    ],
    'installable': True,
    'application': False,
}
