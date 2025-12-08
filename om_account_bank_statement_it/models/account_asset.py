from odoo import models, fields

class AccountMoveInherit(models.Model):
    _inherit = 'account.move'

    def action_post(self):
        for move in self:
            if not move.name or move.name == '/':
                sequence_obj = self.env['ir.sequence'].search([('code', '=', 'account.move')], limit=1)
                if sequence_obj:
                    new_name = f"JP {move.date.strftime('%y / %m')} / {sequence_obj.number_next_actual:03d}"
                    print(f"DEBUG: Nama jurnal yang terbentuk -> {new_name}")  # Debugging
                    move.name = new_name
                    sequence_obj.sudo().write({'number_next_actual': sequence_obj.number_next_actual + 1})
        return super().action_post()

