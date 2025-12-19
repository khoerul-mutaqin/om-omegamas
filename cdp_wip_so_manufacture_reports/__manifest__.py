# -*- coding: utf-8 -*-
{
    "name": "cdp_wip_so_manufacture_reports",
    "summary": "Short (1 phrase/line) summary of the module's purpose",
    "description": """Long description of module's purpose""",
    "author": "My Company",
    "website": "https://www.yourcompany.com",
    # Categories can be used to filter modules in modules listing
    # Check https://github.com/odoo/odoo/blob/15.0/odoo/addons/base/data/ir_module_category_data.xml
    # for the full list
    "category": "Uncategorized",
    "version": "0.1",
    # any module necessary for this one to work correctly
    'depends': [
        'base',
        'product', # Required for product_tmpl_id
        'uom',     # Required for uom_id and category_id
        'stock',   # Recommended since you are doing valuation
        'mrp',     # If you are using MO logic
        'analytic',
        'sale'
    ],    
    # always loaded
    "data": [
        'security/ir.model.access.csv',
        "views/views.xml",
    ],
    # only loaded in demonstration mode
    "demo": [
        "demo/demo.xml",
    ],
}
