{
    'name': 'OM Product Template',
    'version': '1.0',
    'summary': 'Add Custom HWD Fields to Product Template',
    'description': '''
            This module extends the product template by adding custom fields 
            related to HWD (Height, Width, Depth) for better product specification management.
            ''',
    'author': 'A Yazid Bustomi',
    'website': 'https://www.bustomi.my.id/',
    'license': 'LGPL-3',
    'depends': ['base', 'product', 'om_sale_external_id', 'stock_delivery'],
    'data': [
        'views/product_template_form_views.xml',
    ],
    'installable': True,
    'application': False,
}
