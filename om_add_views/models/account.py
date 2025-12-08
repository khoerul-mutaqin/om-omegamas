from odoo import models, fields, api
import re
from odoo.osv.expression import SQL


class AccountInvoiceReport(models.Model):
    _inherit = 'account.invoice.report'

    narration = fields.Text(string="Narration", readonly=True)
    price_unit = fields.Float(string="Unit Price", readonly=True)
    invoice_currency_rate = fields.Float(string="Invoice Currency Rate", readonly=True, digits=(12, 6))
    inverse_rate = fields.Float(
        string="Inverse Rate",
        compute="_compute_inverse_rate",
        readonly=True
    )

    @api.depends('invoice_currency_rate')
    def _compute_inverse_rate(self):
        for record in self:
            record.inverse_rate = 1.0 / record.invoice_currency_rate if record.invoice_currency_rate else 0.0


    _depends = {
        'account.move': ['narration', 'invoice_currency_rate'],
        'account.move.line': ['price_unit'],
    }

    def _select(self) -> SQL:
        return SQL(
            "%s, REPLACE(REGEXP_REPLACE(move.narration, '<[^>]+>', '', 'g'), '&nbsp;', ' ') AS narration, "
            "line.price_unit AS price_unit, move.invoice_currency_rate AS invoice_currency_rate",
            super()._select()
        )


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'

    narration = fields.Html(related='move_id.narration', store=True, readonly=False)
    narration_text = fields.Text(string="Narration (Text)", compute="_compute_narration_text", store=True)

    @api.depends('narration')
    def _compute_narration_text(self):
        for record in self:
            if record.narration:
                record.narration_text = re.sub('<[^<]+?>', '', record.narration)
            else:
                record.narration_text = ""


class AccountMove(models.Model):
    _inherit = 'account.move'

    inverse_rate = fields.Float(
        string="Inverse Rate",
        compute="_compute_inverse_rate",
        readonly=True
    )
    date_order = fields.Datetime(
        string="Order Date",
        readonly=True,
        related='invoice_line_ids.sale_id.date_order'
    )

    amount_total_order = fields.Monetary(
        string="Total SO",
        compute="_compute_amount_total_order",
        currency_field="currency_id",
        store=True
    )
    note_order = fields.Text(
        string="Combined Notes",
        compute="_compute_combined_notes",
        store=True
    )
    sale_name = fields.Char(
        string="Sales Orders",
        compute="_compute_sale_name"
    )

    @api.depends('invoice_line_ids.sale_id.name')
    def _compute_sale_name(self):
        for move in self:
            sale_names = move.invoice_line_ids.mapped('sale_id.name')
            move.sale_name = ", ".join(filter(None, sale_names))
    @api.depends('invoice_line_ids.sale_id.note')
    def _compute_combined_notes(self):
        for move in self:
            notes = move.invoice_line_ids.mapped('sale_id.note')
            clean_notes = [re.sub('<[^<]+?>', '', note or '') for note in notes]
            move.note_order = "\n".join(filter(None, clean_notes))

    @api.depends('invoice_line_ids.sale_id.amount_total')
    def _compute_amount_total_order(self):
        for move in self:
            sale_orders = move.invoice_line_ids.mapped('sale_id')
            move.amount_total_order = sum(sale_orders.mapped('amount_total'))

    @api.depends('invoice_currency_rate')
    def _compute_inverse_rate(self):
        for record in self:
            record.inverse_rate = 1.0 / record.invoice_currency_rate if record.invoice_currency_rate else 0.0
