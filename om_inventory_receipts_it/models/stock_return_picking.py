from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.tools.float_utils import float_compare, float_is_zero, float_round

class StockReturnPicking(models.TransientModel):
    _inherit = 'stock.return.picking'

    def _prepare_move_default_values(self, return_line, new_picking):
        vals = super(StockReturnPicking, self)._prepare_move_default_values(return_line, new_picking)
        
        # Get the original move
        move = return_line.move_id
        
        # Try to get price from purchase order line if it exists
        price = 0.0
        if move.purchase_line_id:
            price = move.purchase_line_id.price_unit
        elif move.origin_returned_move_id and move.origin_returned_move_id.purchase_line_id:
            # If this is a return of return, get price from original purchase
            price = move.origin_returned_move_id.purchase_line_id.price_unit
        else:
            price = move.price_unit

        vals.update({
            'price_unit': price,
            'value': price * return_line.quantity,  # Set the total value
            'remaining_value': price * return_line.quantity,  # Set remaining value
            'remaining_qty': return_line.quantity,  # Set remaining quantity
        })
        
        return vals

    def create_returns(self):
        # Override to ensure price is properly set in return picking
        new_picking_id, pick_type_id = super(StockReturnPicking, self).create_returns()
        
        # Get the new picking and update prices if needed
        new_picking = self.env['stock.picking'].browse(new_picking_id)
        for move in new_picking.move_ids_without_package:
            if move.origin_returned_move_id and move.origin_returned_move_id.purchase_line_id:
                price = move.origin_returned_move_id.purchase_line_id.price_unit
                move.write({
                    'price_unit': price,
                    'value': price * move.product_uom_qty,
                    'remaining_value': price * move.product_uom_qty,
                    'remaining_qty': move.product_uom_qty,
                })
        
        return new_picking_id, pick_type_id

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    def action_create_returns(self):
        # Override to ensure proper price handling in returns
        return_vals = super(StockPicking, self).action_create_returns()
        if return_vals.get('res_id'):
            picking = self.env['stock.picking'].browse(return_vals['res_id'])
            for move in picking.move_ids_without_package:
                if move.origin_returned_move_id and move.origin_returned_move_id.purchase_line_id:
                    price = move.origin_returned_move_id.purchase_line_id.price_unit
                    move.write({
                        'price_unit': price,
                        'value': price * move.product_uom_qty,
                        'remaining_value': price * move.product_uom_qty,
                        'remaining_qty': move.product_uom_qty,
                    })
        return return_vals

    def action_create_exchanges(self):
        # Override to ensure proper price handling in exchanges
        exchange_vals = super(StockPicking, self).action_create_exchanges()
        if exchange_vals.get('res_id'):
            picking = self.env['stock.picking'].browse(exchange_vals['res_id'])
            for move in picking.move_ids_without_package:
                if move.origin_returned_move_id and move.origin_returned_move_id.purchase_line_id:
                    price = move.origin_returned_move_id.purchase_line_id.price_unit
                    move.write({
                        'price_unit': price,
                        'value': price * move.product_uom_qty,
                        'remaining_value': price * move.product_uom_qty,
                        'remaining_qty': move.product_uom_qty,
                    })
        return exchange_vals
