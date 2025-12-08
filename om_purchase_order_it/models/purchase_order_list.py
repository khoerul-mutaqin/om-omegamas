from odoo import fields, models, api


class PurchaseOrderList(models.Model):
    _inherit = 'purchase.order'

    dp_blanket = fields.Float(string="Down Payment")
    dp_order = fields.Float(string="Order Down Payment")
    dp_sisa = fields.Float(string="Remaining Down Payment")
