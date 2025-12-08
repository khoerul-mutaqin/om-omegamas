{
    'name': 'IT Custom PDF Uploads',
    'version': '1.0',
    'summary': 'Add Upload File PDF tab to product form',
    'description': 'Custom module to add an Upload File PDF tab in product form view',
    'author': 'Your Name',
    'website': 'https://yourwebsite.com',
    'category': 'Inventory',
    'depends': ['product'],
    'data': [
        'views/product_template_upload_pdf_views.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
