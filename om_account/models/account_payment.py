# -*- coding: utf-8 -*-

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from odoo.exceptions import UserError

class AccountPayment(models.Model):
    _inherit = 'account.payment'

    # STATE ORI
    state = fields.Selection(
        selection=[
            ('draft', "Draft"),
            ('to_approve', 'To Approve'),
            ('approved', 'Approved'),
            ('in_process', "In Process"),
            ('paid', "Paid"),
            ('canceled', "Canceled"),
            ('rejected', "Rejected"),
        ],
        required=True,
        default='draft',
        compute='_compute_state', store=True, readonly=False,
        copy=False,
    )


    amount = fields.Monetary('Amount to Paid', currency_field='currency_id')
    amount_to_paid = fields.Monetary('Amount', copy=False, currency_field='currency_id')
    # number_of_batch_move = fields.Integer('number_of_batch_move', copy=False)



    def action_to_approve(self):
        ''' draft -> to approve '''
        
        # self.move_id._to_approve()
        self.state = 'to_approve'

    def action_approve(self):
        ''' to approve -> approved '''
        # self.move_id._button_approve()
        self.state = 'approved'

    def unlink(self):
        for rec in self:
            move = self.env['account.move'].search([('id_payments', 'ilike', rec.id), ('amount_total', '=', rec.amount)])
            for m in move:
                int_list = list(map(int, m.id_payments.strip('[]').split(', '))) if m.id_payments else []
                if len(int_list) > 0:
                    int_list.remove(rec.id)
                    m.id_payments = str(int_list)
        return super(AccountPayment, self).unlink()

    @api.constrains('state', 'move_id')
    def _check_move_id(self):
        for payment in self:
            if (
                payment.state not in ('draft', 'canceled', 'to_approve', 'approved')
                and not payment.move_id
                and payment.outstanding_account_id
            ):
                raise ValidationError(_("A payment with an outstanding account cannot be confirmed without having a journal entry."))

    def action_post(self):
        ''' draft -> posted '''
        # Do not allow posting if the account is required but not trusted
        for payment in self:
            if payment.require_partner_bank_account and not payment.partner_bank_id.allow_out_payment:
                raise UserError(_(
                    "To record payments with %(method_name)s, the recipient bank account must be manually validated. "
                    "You should go on the partner bank account of %(partner)s in order to validate it.",
                    method_name=self.payment_method_line_id.name,
                    partner=payment.partner_id.display_name,
                ))
                
            
            # Reconciled
            lines = payment.move_id.invoice_line_ids
            ref = payment.memo
            account_ids = lines.mapped('account_id.id')
            
            line = self.env['account.move.line'].sudo().search([('move_name', '=', ref)])
            # reconciled_lines = False
            entry = False
            
            if line:
                reconciled_lines = line.filtered(lambda l: l.account_id.id in account_ids)
                entry = lines.filtered(lambda l: l.account_id.id == reconciled_lines.account_id.id)
                reconciled_lines |= entry
                entry.move_id.action_post()
                reconciled_lines.reconcile()
            else:
                self.env.cr.execute("""
                    SELECT id
                    FROM account_move
                    WHERE id_payments LIKE '[%s,%%'
                    OR id_payments LIKE '%%, %s,%%'
                    OR id_payments LIKE '%%, %s]'
                    OR id_payments = '[%s]'
                """, (payment.id, payment.id, payment.id, payment.id))
                result = self.env.cr.fetchall()
                move_ids = [row[0] for row in result]
                move = self.env['account.move'].browse(move_ids)
                for m in move:
                    # for lm in m.line_ids:
                    reconciled_lines = m.line_ids.filtered(lambda l: l.account_id.id in account_ids)
                    entry = lines.filtered(lambda l: l.account_id.id == reconciled_lines.account_id.id)
                    reconciled_lines |= entry
                    if not any(aml.reconciled for aml in reconciled_lines):
                        entry.move_id.action_post()
                        reconciled_lines.reconcile()
            
            # Reconciled

    
        
        self.filtered(lambda pay: pay.outstanding_account_id.account_type == 'asset_cash').state = 'paid'
        # Avoid going back one state when clicking on the confirm action in the payment list view and having paid expenses selected
        # We need to set values to each payment to avoid recomputation later
        self.filtered(lambda pay: pay.state in {False, 'draft', 'in_process', 'approved'}).state = 'in_process'

        
    @api.depends('move_id.name', 'state')
    def _compute_name(self):
        for payment in self:
            if payment.id and not payment.name and payment.state in ('to_approve','in_process', 'paid'):
                payment.name = (
                    payment.move_id.name
                    or self.env['ir.sequence'].with_company(payment.company_id).next_by_code(
                        'account.payment',
                        sequence_date=payment.date,
                    )
                )
