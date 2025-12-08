# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AccountPaymentRegister(models.TransientModel):
    _inherit = 'account.payment.register'

    amount_to_paid = fields.Monetary('Amount to Paid', copy=False, currency_field='currency_id')

    
    def _create_payments(self):
        self.ensure_one()
        batches = []
        # Skip batches that are not valid (bank account not setup or not trusted but required)
        for batch in self.batches:
            batch_account = self._get_batch_account(batch)
            if self.require_partner_bank_account and (not batch_account or not batch_account.allow_out_payment):
                continue
            batches.append(batch)

        if not batches:
            raise UserError(_(
                "To record payments with %(payment_method)s, the recipient bank account must be manually validated. You should go on the partner bank account in order to validate it.",
                payment_method=self.payment_method_line_id.name,
            ))

        first_batch_result = batches[0]
        edit_mode = self.can_edit_wizard and (len(first_batch_result['lines']) == 1 or self.group_payment)
        to_process = []

        if edit_mode:
            payment_vals = self._create_payment_vals_from_wizard(first_batch_result)
            to_process_values = {
                'create_vals': payment_vals,
                'to_reconcile': first_batch_result['lines'],
                'batch': first_batch_result,
            }

            # Force the rate during the reconciliation to put the difference directly on the
            # exchange difference.
            if self.writeoff_is_exchange_account and self.currency_id == self.company_currency_id:
                total_batch_residual = sum(first_batch_result['lines'].mapped('amount_residual_currency'))
                to_process_values['rate'] = abs(total_batch_residual / self.amount) if self.amount else 0.0

            to_process.append(to_process_values)
        else:
            if not self.group_payment:
                # Don't group payments: Create one batch per move.
                lines_to_pay = self._get_total_amounts_to_pay(batches)['lines'] if self.installments_mode in ('next', 'overdue', 'before_date') else self.line_ids
                new_batches = []
                for batch_result in batches:
                    for line in batch_result['lines']:
                        if line not in lines_to_pay:
                            continue
                        new_batches.append({
                            **batch_result,
                            'payment_values': {
                                **batch_result['payment_values'],
                                'payment_type': 'inbound' if line.balance > 0 else 'outbound'
                            },
                            'lines': line,
                        })
                batches = new_batches

            for batch_result in batches:
                to_process.append({
                    'create_vals': self._create_payment_vals_from_batch(batch_result),
                    'to_reconcile': batch_result['lines'],
                    'batch': batch_result,
                })

        payments = self._init_payments(to_process, edit_mode=edit_mode)
        move = self.line_ids.move_id
        # count payment in smart button move
        int_list = False
        for mv in move:
            int_list = list(map(int, mv.id_payments.strip('[]').split(', '))) if mv.id_payments and mv.id_payments != '[]' else []
            if len(payments) > 1:
                pay = payments.filtered(lambda x: x.amount == mv.amount_total)
                int_list.extend(pay.ids)
            else:
                int_list.extend(payments.ids)
            mv.id_payments = str(int_list)
        # count payment in smart button move

        # self._post_payments(to_process, edit_mode=edit_mode)
        self._to_approve_payments(to_process)
        # self._reconcile_payments(to_process, edit_mode=edit_mode)
        return payments

        

    
    def _to_approve_payments(self, to_process):
        payments = self.env['account.payment']
        for vals in to_process:
            payments |= vals['payment']
        payments.action_to_approve()

    def _create_payment_vals_from_wizard(self, batch_result):
        res = super()._create_payment_vals_from_wizard(batch_result)
        res['amount_to_paid'] = self.amount
        res['amount'] = self.amount_to_paid
        # res['number_of_batch_move'] = len(batch_result)
        return res
    

    def action_create_payments(self):
        for rec in self:
            if rec.amount_to_paid > rec.amount:
                raise UserError (_('Amount to paid cannot greater than amount'))
        return super().action_create_payments() 