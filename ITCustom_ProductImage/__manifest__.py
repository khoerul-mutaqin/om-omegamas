{
    'name': 'IT Custom Image Uploads',
    'version': '1.0',
    'summary': 'Add Image Upload functionality to product form',
    'description': 'Custom module to add image upload and selection functionality to product form view',
    'author': 'Your Name',
    'website': 'https://yourwebsite.com',
    'category': 'Inventory',
    'depends': ['product', 'documents'],
    'data': [
        'views/product_documents_selection_wizard_views.xml',
        'views/product_image_multi.xml',
        'security/ir.model.access.csv',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}
