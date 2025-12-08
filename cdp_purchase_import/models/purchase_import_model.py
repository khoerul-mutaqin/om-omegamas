from odoo import models, fields, api
from odoo.exceptions import UserError

class PurchaseImportModel(models.Model):
    _name = 'purchase.import'
    _description = 'Purchase Import Model'

    name = fields.Char(string='Name', required=True, help="Name")
    order_number = fields.Integer(string='Order Number', required=True, help="Order number of the purchase")
    product_id = fields.Many2one('product.product', string='Product', required=True, help="Product associated with the purchase")
    quantity = fields.Float(string='Quantity', required=True, help="Quantity of the product purchased")
    serial_number = fields.Char(string='Serial Number', help="Serial number of the product in a form of text")
    purchase_date = fields.Date(string='Purchase Date', required=True, help="Date of the purchase")
    cost = fields.Float(string='Cost', required=True, help="Cost of the product purchased")
    purchase_order_id = fields.Many2one('purchase.order', string='Purchase Order', help="Purchase order associated with the purchase", copy=False)
    cdp_serial_number = fields.Char(string='Serial Number input', help="CDP serial number of the product")
    picking_type_id = fields.Many2one('stock.picking.type', string='Deliver To', required=True, help="Picking type for the purchase to be assigned on PO")
    processed_purchase = fields.Boolean(string='Processed',store=True, copy=False)

    # Datetime.to_datetime(self.x_required_date)

    def action_process_purchase(self):
        #PO step
        if not self.processed_purchase:
            po = self.env['purchase.order'].create(self._prepare_create_values_specific())
            if po:
                po.button_confirm()
            #end PO step
                # serial_number_id = self.create_lot_id()
                order_line = po.order_line
                stock_move = self.env['stock.move'].search([('purchase_line_id', 'in', order_line.ids)])
                stock_move.date = self.purchase_date
                ml = stock_move.move_line_ids[0]
                ml.lot_name = self.serial_number
                #ml.lot_id = self.serial_number_id
                ml.quantity = self.quantity


                picking_id = stock_move.picking_id
                if picking_id:
                    picking_id.button_validate()
                self.processed_purchase = True
                self.purchase_order_id = po.id
                po.active = False
                # raise UserError(po)

    def _prepare_create_values_specific(self):
        return {
            'name': self.name,
            # 'order_number': self.order_number,
            'date_order': self.purchase_date,
            'date_planned': self.purchase_date,
            'partner_id': 7793,
            'picking_type_id': self.picking_type_id.id,
            'order_line': [(0, 0, self._prepare_order_line_values())],

        }
    
    def _prepare_order_line_values(self):
        return {
            'product_id': self.product_id.id,
            'product_qty': self.quantity,
            'price_unit': self.cost,
            'name': self.name or self.product_id.name,
            'date_planned': self.purchase_date,
            'taxes_id':False,
            'cdp_serial_number': self.serial_number,
        }
