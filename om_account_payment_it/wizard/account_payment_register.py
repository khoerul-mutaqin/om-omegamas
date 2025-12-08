from odoo import models, fields, api


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    def action_create_payments(self):
        res = super().action_create_payments()

        payments = self.env["account.payment"].search([("id", "in", self._context.get("active_ids", []))])

        for payment in payments:
            journal_code = payment.journal_id.code if payment.journal_id else "XXX"

            payment_date = payment.date or fields.Date.context_today(self)
            year = payment_date.strftime('%y')
            month = payment_date.strftime('%m')

            sequence = payment._get_next_sequence(journal_code, year, month)
            payment.name = f"{journal_code} {year}/{month}/{sequence}"

        return res  # Tetap kembalikan hasil super() tanpa modifikasi

