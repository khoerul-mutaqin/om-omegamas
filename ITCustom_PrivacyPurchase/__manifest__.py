{
    'name': 'ITCustom Privacy Purchase',
    'version': '1.0',
    'depends': ['purchase'],
    'category': 'Customization',
    'summary': 'Disable editing in Purchase Order Products tab after confirmation',
    'description': 'This module disables editing and adding products in the Purchase Order form after confirmation.',
    'data': [
        'views/purchase_order_views.xml',
    ],
    'installable': True,
    'application': False,
}
