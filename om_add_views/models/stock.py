from odoo import models, fields

class StockMoveLine(models.Model):
    _inherit = 'stock.move.line'

    description_picking = fields.Text(string="Description", related='move_id.description_picking')
