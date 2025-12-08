# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import _, api, fields, models, SUPERUSER_ID
from odoo.exceptions import UserError
from odoo.fields import Command
from odoo.tools import format_date, frozendict

class AccountMove(models.Model):
    _inherit = 'account.move.line'

    sale_id = fields.Many2one('sale.order', string='Sale Order', copy=False)
   