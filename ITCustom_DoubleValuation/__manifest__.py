{
    'name': 'IT Custom Double Valuation Fix',
    'version': '18.0.1.0.0',
    'category': 'Manufacturing',
    'summary': 'Fix double valuation issue when creating backorder in manufacturing',
    'description': """
        Fix untuk masalah valuation ganda saat create backorder pada Manufacturing Orders.
        Problem: Saat partial validate 10 dari 100, sistem membuat valuation untuk 10 dan 100.
        Solution: Hanya buat valuation untuk quantity yang divalidasi saja (10).
    """,
    'author': 'IT Department',
    'website': 'https://omegamas.com',
    'depends': ['stock', 'stock_account', 'mrp'],
    'data': [],
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}
