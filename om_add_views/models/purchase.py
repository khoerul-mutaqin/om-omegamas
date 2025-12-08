from odoo import models, fields
from odoo.osv.expression import SQL


class PurchaseReport(models.Model):
    _inherit = 'purchase.report'

    receipt_status = fields.Selection([
        ('pending', 'Not Received'),
        ('partial', 'Partially Received'),
        ('full', 'Fully Received'),
    ], string="Receipt Status")

    invoice_status = fields.Selection([
        ('no', 'Nothing to Bill'),
        ('to invoice', 'Waiting Bills'),
        ('invoiced', 'Fully Billed'),
    ], string="Invoice Status")

    dp_blanket = fields.Float(string="Down Payment", readonly=True, related="order_id.dp_blanket")
    partner_ref = fields.Char(string="Vendor Reference", readonly=True, related="order_id.partner_ref")

    def _select(self) -> SQL:
        return SQL(
            """
                %s,
                po.receipt_status as receipt_status,
                po.invoice_status as invoice_status
            """,
            super()._select()
        )

    def _group_by(self) -> SQL:
        return SQL(
            "%s, po.receipt_status, po.invoice_status",
            super()._group_by()
        )
