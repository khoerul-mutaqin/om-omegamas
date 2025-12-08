# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import fields, models, api
from odoo.tools import float_compare, float_is_zero
from odoo.tools.misc import groupby

# class ProductProduct(models.Model):
#     _inherit = "product.product"

#     min_order_qty = fields.Float('Min Qty', compute='_compute_min_order_qty')


#     def _compute_min_order_qty(self):
#         for rec in self:
#             order_point = self.env['stock.warehouse.orderpoint'].search([('product_id', '=', rec.id)])
#             if order_point:
#                 rec.min_order_qty = order_point.product_min_qty
#             else:
#                 rec.min_order_qty = 0
