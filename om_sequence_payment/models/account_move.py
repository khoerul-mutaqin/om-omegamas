from odoo import models, fields


class AccountMove(models.Model):
    _inherit = 'account.move'

    # def action_post(self):
    #     res = super(AccountMove, self).action_post()
    #     for rec in self:
    #         if not rec.name:
    #             if rec.journal_id and self.journal_id.type == 'general' and rec.move_type == 'entry':
    #                 # rec.name = self.env['ir.sequence'].next_by_code('jv.sequence')
    #                 rec.name = self.get_om_sequence('jv.sequence')
    #             elif rec.move_type == 'out_invoice':
    #                 # rec.name = self.env['ir.sequence'].next_by_code('si.sequence')
    #                 rec.name = self.get_om_sequence('si.sequence')
    #             elif rec.move_type == 'in_invoice':
    #                 # rec.name = self.env['ir.sequence'].next_by_code('pi.sequence')
    #                 rec.name = self.get_om_sequence('pi.sequence')
    #     return res
    
    

    # def get_om_sequence(self, code):
    #     if self.invoice_date:
    #         inv_date_obj = fields.Date.from_string(self.invoice_date)
    #         year = inv_date_obj.year
    #         month = f"{inv_date_obj.month:02d}"
    #         code = code
    #         sequence_code = f'{code}.{year}.{month}'
    #         sequence = self.env['ir.sequence'].search([('code', '=', sequence_code)], limit=1)
    #         if not sequence:
    #             self.env['ir.sequence'].create({
    #                 'name': 'OM Sequence',
    #                 'code': f'{code}.{year}.{month}',
    #                 'prefix': f'{code.split('.')[0].upper()} {year}/{month}/',
    #                 'suffix': '',
    #                 'padding': 3,
    #                 'number_next': 1,
    #                 'number_increment': 1,
    #                 'use_date_range': True,
    #                 'implementation': 'no_gap',
    #             })
    #         return self.env['ir.sequence'].next_by_code(sequence_code)
