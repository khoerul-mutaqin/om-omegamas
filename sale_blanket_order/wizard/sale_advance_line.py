# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tools import format_date, frozendict


class SaleAdvancePaymentInvLine(models.TransientModel):
    _name = 'sale.advance.payment.inv.line'

    advance_payment_id = fields.Many2one('sale.advance.payment.inv')
    sale_id = fields.Many2one('sale.order', 'Order')
    dp_blanket = fields.Float('Down Payment', related='sale_id.dp_blanket')
    dp_order = fields.Float(string="Order Down Payment")
    dp_sisa = fields.Float(string="Remaining Down Payment", related='sale_id.dp_sisa')
    client_order_ref = fields.Char(
        string="Customer Reference",
        related='sale_id.client_order_ref',
        readonly=True
    )

    # advance_payment_method = fields.Selection(
    #     selection=[
    #         ('delivered', "Regular invoice"),
    #         ('percentage', "Down payment (percentage)"),
    #         ('fixed', "Down payment (fixed amount)"),
    #     ],
    #     string="Payment Type",
    #     related='advance_payment_id.advance_payment_method'
    #     )
