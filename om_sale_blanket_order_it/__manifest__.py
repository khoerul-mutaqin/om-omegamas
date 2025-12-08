{
    'name': 'OM Sales Blanket Order IT',
    'version': '1.0',
    'summary': 'Add Backdate Feature and Custom Sales Fields to Blanket Orders',
    'description': '''
        This module enhances the Sales Blanket Order process by:
        - Enabling backdating for improved control over sales timelines
        - Adding necessary custom fields to support sales and accounting needs
        - Improving the interface with wizard support and list view enhancements
        ''',
    'author': 'A Yazid Bustomi',
    'website': 'https://www.bustomi.my.id/',
    'license': 'LGPL-3',
    'depends': ['sale_blanket_order', 'account', 'stock', 'om_sale_external_id'],
    'data': [
        'security/ir.model.access.csv',
        'reports/pro_forma_reports.xml',
        'reports/report_pro_forma_invoice_template_with_photo.xml',
        'reports/report_pro_forma_invoice_template_no_photo.xml',
        'reports/report_mpo.xml',
        'reports/report_mto_draft.xml',
        'views/sale_blanket_order_line_views.xml',
        'views/sale_blanket_order_views.xml',
        'views/sale_blanket_order_tree.xml',
        'wizard/sale_blanket_order_wizard_views.xml',
        'wizard/request_dp_blanket_order_view.xml',
    ],
    'installable': True,
    'application': False,
}
