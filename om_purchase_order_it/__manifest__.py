{
    'name': 'OM Purchase Order IT',
    'version': '1.0',
    'summary': 'Add Sequential Draft Numbers, Manual Delivery, Accounting Fields, and Global Discount to Purchase Orders',
    'description': '''
            This module enhances the Purchase Order process by:
            - Creating sequential names for draft PO
            - Supporting manual stock picking for deliveries
            - Adding required accounting fields
            - Introducing a global discount feature with wizard support
            ''',
    'category': 'Purchase Order',
    'author': 'A Yazid Bustomi',
    'website': 'https://www.bustomi.my.id/',
    'license': 'LGPL-3',
    'depends': ['purchase', 'om_purchase_manual_delivery', 'account', 'stock', 'mrp'],
    "data": [
            "security/ir.model.access.csv",
            "wizard/alert_confirm_order_views.xml",
            "views/purchase_order_line_views.xml",
            "views/purchase_order_list_views.xml",
            "views/purchase_order_views.xml",
            "wizard/purchase_order_discount_views.xml"
        ],
    'installable': True,
    'auto_install': False
}