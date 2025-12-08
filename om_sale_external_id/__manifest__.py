{
    'name': 'Om Sale External ID',
    'version': '1.0',
    'summary': 'Add External Product ID Mapping for Sales',
    'description': '''
        This module allows you to manage and associate external product IDs 
        for use in sales orders and integration with external systems.
        ''',
    'category': 'Sales',
    'author': 'A Yazid Bustomi',
    'website': 'https://www.bustomi.my.id/',
    'license': 'LGPL-3',
    'depends': ['sale',],
    'data': [
        'security/ir.model.access.csv',
        'views/external_id_views.xml',
    ],
    'installable': True,
    'auto_install': False
}
