from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'
    
    is_manufacturing_op = fields.Boolean(
        string='Is Manufacturing Operation',
        compute='_compute_is_manufacturing_op'
    )
    
    @api.depends('move_ids', 'move_ids.raw_material_production_id', 'move_ids.production_id')
    def _compute_is_manufacturing_op(self):
        for picking in self:
            manufacturing_moves = picking.move_ids.filtered(
                lambda m: m.raw_material_production_id or m.production_id
            )
            picking.is_manufacturing_op = bool(manufacturing_moves)
