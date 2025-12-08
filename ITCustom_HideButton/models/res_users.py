# -*- coding: utf-8 -*-
from odoo import api, fields, models

class ResUsers(models.Model):
    """
    Model to handle hiding specific buttons for certain users.
    """
    _inherit = 'res.users'

    hide_button_ids = fields.Many2many(
        'itcustom.button', 
        string="Hidden Buttons",
        store=True, 
        help='Select button items that need to be hidden to this user.',
        # Pastikan nama tabel relasional sama
        relation='itcustom_button_res_users_rel',
        column1='res_users_id',
        column2='itcustom_button_id'
    )

    @api.model
    def create(self, vals):
        """
        Create method to handle initial synchronization
        """
        user = super(ResUsers, self).create(vals)
        # Sinkronisasi setelah create jika ada hide_button_ids
        if 'hide_button_ids' in vals:
            user._sync_hide_buttons()
        return user

    def write(self, vals):
        """
        Write method for the ResUsers model.
        Sync hide_button_ids with buttons' restrict_user_ids.
        """
        res = super(ResUsers, self).write(vals)
        if 'hide_button_ids' in vals and not self.env.context.get('syncing_hide_buttons'):
            self._sync_hide_buttons()
        return res

    def _sync_hide_buttons(self):
        """
        Synchronize hide_button_ids with the relational table
        """
        for record in self:
            # Dapatkan semua button yang terkait dengan user ini
            related_buttons = record.hide_button_ids
            
            # Update restrict_user_ids di button side
            for button in related_buttons:
                button.with_context(syncing_hide_buttons=True).write({
                    'restrict_user_ids': [(4, record.id)]
                })
            
            # Handle unlinked buttons
            previous_buttons = self.env['itcustom.button'].search([
                ('restrict_user_ids', 'in', [record.id])
            ])
            removed_buttons = previous_buttons - related_buttons
            for button in removed_buttons:
                button.with_context(syncing_hide_buttons=True).write({
                    'restrict_user_ids': [(3, record.id)]
                })