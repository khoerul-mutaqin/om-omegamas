{
    'name': 'ITCustom RFQ Quantity Validation',
    'version': '18.0.1.0.0',
    'category': 'Purchase Management',
    'summary': 'Ensure RFQ product_qty does not exceed remaining quantity in purchase.request.line when creating RFQ from purchase request',
    'description': """
        This module adds validation in the Purchase Request to RFQ wizard.
        When creating an RFQ (Purchase Order draft) from purchase.request.line,
        the product_qty in the wizard item cannot exceed the remaining quantity (original minus already allocated) in the purchase.request.line.
        This prevents over-ordering across multiple RFQs.
    """,
    'author': 'ITCustom',
    'website': '',
    'depends': ['om_purchase_request'],
    'data': [
        'views/purchase_request_line_make_purchase_order_view.xml',
    ],
    'demo': [],
    'installable': True,
    'auto_install': False,
    'application': False,
    'license': 'LGPL-3',
}
