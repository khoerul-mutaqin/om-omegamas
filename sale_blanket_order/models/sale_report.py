# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models

from odoo.addons.sale.models.sale_order import SALE_ORDER_STATE


class SaleReport(models.Model):
    _inherit = "sale.report"

    dp_blanket = fields.Float(
        string="Down Payment", readonly=True, copy=False,
        compute="_compute_dp_from_so"
        # related="blanket_order_id.down_payment",
    )
    dp_order = fields.Float(
        string="Order Down Payment", readonly=True, copy=False,
        compute="_compute_dp_from_so"
    )
    dp_sisa = fields.Float(
        string="Remaining Down Payment", readonly=True, copy=False,
        compute="_compute_dp_from_so"
    )

    def _compute_dp_from_so(self):
        for rec in self:
            dp_blanket = 0
            dp_order = 0
            dp_sisa = 0
            so = self.env['sale.order'].search([('id', '=', rec.order_reference.id)])
            if so:
                dp_blanket = so.dp_blanket
                dp_order = so.dp_order
                dp_sisa = so.dp_sisa
            rec.update({
                'dp_blanket': dp_blanket,
                'dp_order': dp_order,
                'dp_sisa': dp_sisa
            })
 