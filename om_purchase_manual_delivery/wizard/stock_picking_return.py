# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, Command, fields, models
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_is_zero


class ReturnPicking(models.TransientModel):
    _inherit = "stock.return.picking"

    is_from_purchase = fields.Boolean('From Purchase', compute='_is_from_purchase')

    
    @api.depends('product_return_moves')
    def _is_from_purchase(self):
        for line in self:
            line.is_from_purchase = bool(line.product_return_moves.mapped('move_id.purchase_line_id.id'))


class ReturnPickingLine(models.TransientModel):
    _inherit = "stock.return.picking.line"

    purchase_id = fields.Many2one('purchase.order', string='Purchase Order', related='move_id.purchase_line_id.order_id')
    qty_purchase_order = fields.Float('Qty Order', related='move_id.purchase_line_id.product_qty')
    qty_receipt_order = fields.Float('Receipt Qty', related='move_id.quantity')
    