from odoo import models, fields


class AccountMove(models.Model):
    """
    Model to extend account.move for hiding buttons based on user.
    """
    _inherit = 'account.move'

    def _compute_hide_pay_button(self):
        """
        Compute method to check if the Pay button should be hidden for the current user.
        """
        for record in self:
            record.hide_pay_button = bool(
                self.env.user.hide_button_ids.filtered(
                    lambda b: b.model == 'account.move' and b.button_name == 'action_register_payment'
                )
            )

    hide_pay_button = fields.Boolean(
        compute='_compute_hide_pay_button',
        string='Hide Pay Button',
        help='Whether to hide the Pay button for the current user.'
    )
