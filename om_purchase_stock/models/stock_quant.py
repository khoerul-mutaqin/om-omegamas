from odoo import api, models, fields

class StockQuant(models.Model):
    _inherit = 'stock.quant'

    no_ttb = fields.Text('Description')
    min_order_qty = fields.Float('Min Qty', compute='_compute_min_order_qty')

    @api.model
    def _get_inventory_fields_write(self):
        res = super(StockQuant, self)._get_inventory_fields_write()
        """ Returns a list of fields user can edit when he want to edit a quant in `inventory_mode`.
        """
        res.append('no_ttb')
        return res

    def _compute_min_order_qty(self):
        for rec in self:
            order_point = self.env['stock.warehouse.orderpoint'].search([('product_id', '=', rec.product_id.id), ('location_id', '=', rec.location_id.id)])
            if order_point:
                rec.min_order_qty = order_point.product_min_qty
            else:
                rec.min_order_qty = 0

    def _get_inventory_move_values(self, qty, location_id, location_dest_id, package_id=False, package_dest_id=False):
        res = super(StockQuant, self)._get_inventory_move_values(qty, location_id, location_dest_id, package_id, package_dest_id)
        if res['move_line_ids']:
            res['move_line_ids'][0][2]['no_ttb'] = self.no_ttb
        return res