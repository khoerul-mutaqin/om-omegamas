# encoding: utf-8
# Part of Odoo - CLuedoo Edition. Ask Falinwa / CLuedoo representative for full copyright And licensing details.
{
    "name": "Disallow negative stock",
    "version": "18.0.0.0.0",
    "category": "Inventory, Stock",
    "license": "OPL-1",
    "summary": "Disallow negative stock levels",
    "author": "CLuedoo",
    "website": "https://www.cluedoo.com/shop/lic-clu-set-inv-0016-prevent-negative-stock-6454",
    "support": "support@cluedoo.com",
    "depends": ["stock"],
    "data": [
        "views/product_product_views.xml",
         "views/stock_location_views.xml"
         ],
    "installable": True,
    "price": 100.0,
    "currency": "USD",
}
