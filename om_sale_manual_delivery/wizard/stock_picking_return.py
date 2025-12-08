# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, Command, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero


class ReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    is_from_sale = fields.Boolean('From Sale', compute='_is_from_sale')

    
    @api.depends('product_return_moves')
    def _is_from_sale(self):
        for line in self:
            line.is_from_sale = bool(line.product_return_moves.mapped('move_id.sale_line_id.id'))

class ReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"

    sale_id = fields.Many2one('sale.order', string='Sale Order', related='move_id.sale_line_id.order_id')
    qty_sale_order = fields.Float('Sale Qty', related='move_id.sale_line_id.product_uom_qty')
    qty_delivery_order = fields.Float('Delivered Qty', related='move_id.quantity')

   