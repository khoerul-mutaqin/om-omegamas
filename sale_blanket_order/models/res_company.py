# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tools import format_date, frozendict

class ResCompany(models.Model):
    _inherit = 'res.company'

    sale_down_payment_product_id = fields.Many2one(
        comodel_name='product.product',
        string="Deposit Product",
        domain=[
            ('type', '=', 'service'),
            ('invoice_policy', '=', 'order'),
        ],
        help="Default product used for down payments",
        check_company=True,
    )

   