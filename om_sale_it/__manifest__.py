{
    'name': 'OM Sales Order IT',
    'version': '1.0',
    'summary': 'Enhancements for Sales Order Form, Fields, and Actions',
    'description': '''
        This module enhances the Sales Order by adding required custom fields, 
        additional validation, and custom views for better order management.
        It also integrates with the Blanket Order functionality.
        ''',
    'author': 'A Yazid Bustomi',
    'website': 'https://www.bustomi.my.id/',
    'license': 'LGPL-3',
    'depends': ['sale', 'stock', 'om_sale_blanket_order_it'],
    'data': [
        'security/ir.model.access.csv',
        'reports/sub_so_reports.xml',
        'reports/report_sub_so_template_with_photo.xml',
        'reports/report_mto_so_template.xml',
        'reports/report_omd_template.xml',
        'wizard/alert_action_confirm_views.xml',
        'views/sale_order_views.xml',
        'views/sale_order_form_line_views.xml',
        'views/sale_order_tree_closed_views.xml',
    ],
    'installable': True,
    'application': False,
}
