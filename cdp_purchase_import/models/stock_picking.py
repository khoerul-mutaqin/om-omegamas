from odoo import models, fields

class StockPicking(models.Model):
    _inherit = "stock.picking"
    
    active = fields.Boolean(string='active', default=True)
