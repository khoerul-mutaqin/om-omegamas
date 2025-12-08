# Copyright 2019 ForgeFlow S.L.
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import api, fields, models
from odoo.tools import float_compare


class StockMove(models.Model):
    _inherit = "stock.move"

    purchase_id = fields.Many2one('purchase.order', string='Purchase Order', related='purchase_line_id.order_id')