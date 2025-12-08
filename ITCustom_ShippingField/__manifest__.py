{
    'name': 'ITCustom Shipping Field',
    'version': '1.0',
    'summary': 'Add Buyer field to stock.picking.batch',
    'description': '''
        This module adds a Buyer field to the stock.picking.batch model.
        The Buyer field is a selection from contacts.
    ''',
    'author': 'ITCustom',
    'website': 'https://www.itcustom.my.id/',
    'license': 'LGPL-3',
    'depends': ['stock_picking_batch'],
    'data': [
        'views/stock_picking_batch_views.xml',
    ],
    'installable': True,
    'application': False,
}
