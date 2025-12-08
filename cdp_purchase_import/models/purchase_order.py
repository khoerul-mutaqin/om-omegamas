from odoo import models, fields

class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    # Add your custom fields or methods below
    # example:
    cdp_serial_number = fields.Char(string='CDP Serial Number', help="CDP serial number of the product")
    
class PurchaseOrder(models.Model):
    _inherit = 'purchase.order'

    active = fields.Boolean(string='active', default=True)
