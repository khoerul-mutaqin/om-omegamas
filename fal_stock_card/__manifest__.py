{
    "name": "Stock Card",
    'version': '18.0.0.0.0',
    "license": "OPL-1",
    'summary': "Displays Stock Card Per Item Per Warehouse and Stock Card Summary List Per Warehouse.",
    "category": 'Inventory',
    "author": "CLuedoo",
    "website": "https://www.cluedoo.com/shop/lic-clu-set-invc-0007-stock-card-5275",
    "support": "support@cluedoo.com",
    "description": """
        this module to display stock card per item per Warehouse
        ==============================================================

        Report by product with quantity and details of stock moves between selected starting and ending dates.
        ==============================================================
        v13.3

        add filtered calculate summary by option
    """,
    "depends": [
        "stock_account",
    ],
    "data": [
        "data/ir_sequence.xml",
        "security/ir.model.access.csv",
        "view/menu.xml",
        "view/stock_card.xml",
        "view/stock_summary.xml",
        "report/stock_card.xml",
    ],
    'images': [
        'static/description/stock_card_screenshot.png'
    ],
    'demo': [
    ],
    "price": 150.0,
    "currency": "USD",
    'application': False,
}
