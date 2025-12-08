from odoo import models, fields, api


class AccountMove(models.Model):
    _inherit = 'account.move'
    
    latest_payment_date = fields.Date('Latest Payment Date', 
        compute='_compute_latest_payment_date' )
    
    @api.depends('line_ids.matched_debit_ids.debit_move_id.payment_id','line_ids.matched_credit_ids.credit_move_id.payment_id')
    def _compute_latest_payment_date(self):
        for record in self:
            if record.move_type != 'in_invoice':
                record.latest_payment_date = False
                continue

            payment_dates = []
            for line in record.line_ids:
                # matched_debit_ids
                for match in line.matched_debit_ids:
                    payment = match.debit_move_id.payment_id
                    if payment:
                        payment_dates.append(payment.date)

                # matched_credit_ids
                for match in line.matched_credit_ids:
                    payment = match.credit_move_id.payment_id
                    if payment:
                        payment_dates.append(payment.date)

            record.latest_payment_date = max(payment_dates) if payment_dates else False