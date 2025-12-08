from odoo import models, fields


class PurchaseOrder(models.Model):
    """
    Model to extend purchase.order for hiding buttons based on user.
    """
    _inherit = 'purchase.order'

    def _compute_hide_confirm_button(self):
        """
        Compute method to check if the Confirm Order button should be hidden for the current user.
        """
        for record in self:
            record.hide_confirm_button = bool(
                self.env.user.hide_button_ids.filtered(
                    lambda b: b.model == 'purchase.order' and b.button_name == 'button_confirm_manual'
                )
            )

    hide_confirm_button = fields.Boolean(
        compute='_compute_hide_confirm_button',
        string='Hide Confirm Button',
        help='Whether to hide the Confirm Order button for the current user.'
    )
