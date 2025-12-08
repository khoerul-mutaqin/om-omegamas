from odoo import models, fields


class PurchaseRequest(models.Model):
    """
    Model to extend purchase.request for hiding buttons based on user.
    """
    _inherit = 'purchase.request'

    def _compute_hide_approve_button(self):
        """
        Compute method to check if the Approve button should be hidden for the current user.
        """
        for record in self:
            record.hide_approve_button = bool(
                self.env.user.hide_button_ids.filtered(
                    lambda b: b.model == 'purchase.request' and b.button_name == 'button_approved'
                )
            )

    def _compute_hide_reset_button(self):
        """
        Compute method to check if the Reset button should be hidden for the current user.
        """
        for record in self:
            record.hide_reset_button = bool(
                self.env.user.hide_button_ids.filtered(
                    lambda b: b.model == 'purchase.request' and b.button_name == 'button_draft'
                )
            )

    hide_approve_button = fields.Boolean(
        compute='_compute_hide_approve_button',
        string='Hide Approve Button',
        help='Whether to hide the Approve button for the current user.'
    )

    hide_reset_button = fields.Boolean(
        compute='_compute_hide_reset_button',
        string='Hide Reset Button',
        help='Whether to hide the Reset button for the current user.'
    )
