from odoo import api, fields, models, _
from odoo.exceptions import ValidationError


class AddProductsWizard(models.TransientModel):
    _name = 'add.products.wizard'
    _description = 'Add Products from Purchase Order Wizard'

    picking_id = fields.Many2one('stock.picking', string='Receipt', required=True)
    partner_id = fields.Many2one('res.partner', string='Vendor')
    purchase_order_id = fields.Many2many('purchase.order', string='Purchase Orders',
                                        domain="[('partner_id', '=', partner_id), ('state', '=', 'purchase')]")
    company_id = fields.Many2one('res.company', related='picking_id.company_id', readonly=True)
    line_ids = fields.One2many('add.products.wizard.line', 'wizard_id', string='Products')

    @api.onchange('partner_id')
    def _onchange_partner_id(self):
        self.purchase_order_id = False
        self.line_ids = [(5, 0, 0)]

    @api.onchange('purchase_order_id')
    def _onchange_purchase_order(self):
        self.ensure_one()
        self.line_ids = [(5, 0, 0)]  # Clear existing lines
        if self.purchase_order_id:
            vals = []
            for po in self.purchase_order_id:
                for line in po.order_line:
                    if line.product_id.type != 'service' and line.product_qty > line.qty_received:
                        remaining_qty = line.product_qty - line.qty_received
                        vals.append((0, 0, {
                            'product_id': line.product_id.id,
                            'purchase_line_id': line.id,
                            'quantity': remaining_qty,
                            'ordered_qty': line.product_qty,
                            'received_qty': line.qty_received,
                            'selected': False,
                        }))
            if vals:
                self.line_ids = vals

    def action_confirm(self):
        self.ensure_one()
        selected_lines = self.line_ids.filtered(lambda l: l.selected)
        if not selected_lines:
            raise ValidationError(_('Please select at least one product.'))

        # Set partner_id from selected vendor
        self.picking_id.partner_id = self.partner_id.id

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
                'purchase_line_id': line.purchase_line_id.id,
            })
        return {'type': 'ir.actions.act_window_close'}


class AddProductsWizardLine(models.TransientModel):
    _name = 'add.products.wizard.line'
    _description = 'Add Products from Purchase Order Wizard Line'

    wizard_id = fields.Many2one('add.products.wizard', string='Wizard')
    po_name = fields.Char(related='purchase_line_id.order_id.name', string='Purchase Order', readonly=True)
    product_id = fields.Many2one('product.product', string='Product', required=True)
    product_description = fields.Char(compute='_compute_product_description', string='Description', readonly=True)
    purchase_line_id = fields.Many2one('purchase.order.line', string='Purchase Order Line')
    ordered_qty = fields.Float(string='Ordered Quantity', readonly=True)
    received_qty = fields.Float(string='Received Quantity', readonly=True)
    quantity = fields.Float(string='Quantity to Add')
    selected = fields.Boolean(string='Select')

    @api.depends('purchase_line_id')
    def _compute_product_description(self):
        for line in self:
            if hasattr(line.purchase_line_id, 'purchase_request_line_id') and line.purchase_line_id.purchase_request_line_id:
                line.product_description = line.purchase_line_id.purchase_request_line_id.name
            else:
                line.product_description = line.purchase_line_id.name
