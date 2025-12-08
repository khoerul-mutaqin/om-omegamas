from odoo import models, fields, api

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    sale_id = fields.Many2one('sale.order', string='Sale Order', compute='_compute_sale_id', store=True)

    @api.depends('group_id')
    def _compute_sale_id(self):
        for picking in self:
            picking.sale_id = picking.group_id.sale_id if picking.group_id else False
