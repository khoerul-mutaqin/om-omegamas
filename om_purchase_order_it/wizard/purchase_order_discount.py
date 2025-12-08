# purchase_discount_wizard.py

from odoo import models, fields, api


class PurchaseOrderDiscount(models.TransientModel):
    _name = 'purchase.order.discount'
    _description = 'Purchase Discount Wizard'

    discount_type = fields.Selection([
        ('percent', 'Percent Discount'),
        ('fixed', 'Fixed Amount')
    ], string='Discount Type', required=True, default='percent')
    discount_amount = fields.Float('Discount Amount', default=0.0)
    discount_percentage = fields.Float('Discount Percentage', default=0.0)

    def apply_discount(self):
        purchase_order = self.env['purchase.order'].browse(self.env.context.get('active_id'))
        discount_product = self.env['product.product'].with_context(active_test=False).search([('default_code', '=', 'DISCOUNT')], limit=1)

        if discount_product:
            if not discount_product.active:
                discount_product.active = True
        else:
            discount_product = self.env['product.product'].create({
                'name': 'Discount',
                'default_code': 'DISCOUNT',
                'type': 'service',
                'purchase_ok': True
            })

        if self.discount_type == 'percent':
            discount_value = round(purchase_order.amount_untaxed * self.discount_percentage, 2)
            discount_percentage_print = self.discount_percentage * 100
            discount_line = {
                'order_id': purchase_order.id,
                'product_id': discount_product.id,
                'name': f'Percent Discount {discount_percentage_print}%',
                'product_qty': 1,
                'price_unit': -discount_value,
            }
        elif self.discount_type == 'fixed':
            discount_line = {
                'order_id': purchase_order.id,
                'product_id': discount_product.id,
                'name': f'Fixed Discount {self.discount_amount}',
                'product_qty': 1,
                'price_unit': -self.discount_amount,
            }

        self.env['purchase.order.line'].create(discount_line)
