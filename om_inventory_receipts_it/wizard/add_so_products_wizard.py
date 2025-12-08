from odoo import api, fields, models, _
from odoo.exceptions import ValidationError

class AddSOProductsWizard(models.TransientModel):
    _name = 'add.so.products.wizard'
    _description = 'Add Products from Sales Order Wizard'

    picking_id = fields.Many2one('stock.picking', string='Delivery Order', required=True)
    sale_order_id = fields.Many2one('sale.order', string='Sales Order', 
                                   domain="[('state', '=', 'sale')]")
    line_ids = fields.One2many('add.so.products.wizard.line', 'wizard_id', string='Products')

    @api.onchange('sale_order_id')
    def _onchange_sale_order(self):
        self.ensure_one()
        self.line_ids = [(5, 0, 0)]  # Clear existing lines
        if self.sale_order_id:
            vals = []
            for line in self.sale_order_id.order_line:
                if line.product_id.type != 'service' and line.product_uom_qty > line.qty_delivered:
                    remaining_qty = line.product_uom_qty - line.qty_delivered
                    vals.append((0, 0, {
                        'product_id': line.product_id.id,
                        'sale_line_id': line.id,
                        'quantity': remaining_qty,
                        'ordered_qty': line.product_uom_qty,
                        'delivered_qty': line.qty_delivered,
                        'selected': False,
                    }))
            if vals:
                self.line_ids = vals

    def action_confirm(self):
        self.ensure_one()
        selected_lines = self.line_ids.filtered(lambda l: l.selected)
        if not selected_lines:
            raise ValidationError(_('Please select at least one product.'))
            
        for line in selected_lines:
            # Create stock move for each selected product
            self.env['stock.move'].create({
                'name': line.product_id.name,
                'product_id': line.product_id.id,
                'product_uom_qty': line.quantity,
                'product_uom': line.product_id.uom_id.id,
                'picking_id': self.picking_id.id,
                'location_id': self.picking_id.location_id.id,
                'location_dest_id': self.picking_id.location_dest_id.id,
                'sale_line_id': line.sale_line_id.id,
            })
        return {'type': 'ir.actions.act_window_close'}


class AddSOProductsWizardLine(models.TransientModel):
    _name = 'add.so.products.wizard.line'
    _description = 'Add Products from Sales Order Wizard Line'

    wizard_id = fields.Many2one('add.so.products.wizard', string='Wizard')
    product_id = fields.Many2one('product.product', string='Product', required=True)
    sale_line_id = fields.Many2one('sale.order.line', string='Sales Order Line')
    ordered_qty = fields.Float(string='Ordered Quantity', readonly=True)
    delivered_qty = fields.Float(string='Delivered Quantity', readonly=True)
    quantity = fields.Float(string='Quantity to Add')
    selected = fields.Boolean(string='Select')
