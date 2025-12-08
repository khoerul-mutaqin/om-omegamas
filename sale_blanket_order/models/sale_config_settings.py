# Copyright 2018 ACSONE SA/NV
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl).

from odoo import fields, models


class SaleConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    group_blanket_disable_adding_lines = fields.Boolean(
        string="Disable adding more lines to SOs",
        implied_group="sale_blanket_order.blanket_orders_disable_adding_lines",
    )
    deposit_default_product_id = fields.Many2one(
        related='company_id.sale_down_payment_product_id',
        readonly=False,
        # previously config_parameter='sale.default_deposit_product_id',
    )


