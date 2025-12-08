{
    'name': 'ITCustom Report Shipping',
    'version': '1.0',
    'summary': 'Shipping Reports for Batch Transfers',
    'description': '''
        This module provides shipping reports for Batch Transfers.
        - Commercial Invoice
        - Packing List
        - Invoice Document
    ''',
    'author': 'ITCustom',
    'website': 'https://www.itcustom.my.id/',
    'license': 'LGPL-3',
    'depends': ['stock_picking_batch', 'ITCustom_ShippingField'],
    'data': [
        'reports/commercial_invoice.xml',
        'reports/packing_list.xml',
        'reports/invoice_doc.xml',
        'reports/packing_list_buyer_bern.xml',
        'reports/invoice_doc_buyer_bern.xml',
        'reports/shipping_plan.xml',
        'reports/report_actions.xml',
    ],
    'assets': {
        'web.report_assets_pdf': [
            'ITCustom_ReportShipping/static/src/img/SICS.png',
            'ITCustom_ReportShipping/static/src/img/svlk.png',
        ],
    },
    'installable': True,
    'application': False,
}
