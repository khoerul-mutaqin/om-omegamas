{
    'name': 'IT Custom Print PO Decimal',
    'version': '1.0',
    'category': 'Purchase',
    'summary': 'Remove trailing zeros from QTY in Purchase Order print',
    'depends': ['purchase'],
    'data': [
        'reports/purchase_order_report.xml',
    ],
    'installable': True,
    'application': False,
}
