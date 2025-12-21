# -*- coding: utf-8 -*-
{
    "name": "WIP SO Manufacture Report",
    "version": "18.0.0.0.0",
    "description": """
        Calculate WIP SO Manufacture Reports Stock Valuation
    """,
    "category": "General",
    "author": "CLuedoo",
    "website": "www.cluedoo.com",
    "support": "support@cluedoo.com",
    'depends': [
        'base',
        'product',
        'uom',     
        'stock',  
        'mrp',    
        'analytic',
        'sale'
    ],    
    # always loaded
    "data": [
        'security/ir.model.access.csv',
        "views/views.xml",
    ],
    # only loaded in demonstration mode
    #"demo": [],
}
