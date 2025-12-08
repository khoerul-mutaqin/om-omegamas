from odoo import api, fields, models


class SaleOrder(models.Model):
    """
    Extend sale.order to add computed field for hiding Confirm button.
    """
    _inherit = 'sale.order'

    @api.depends('state')
    def _compute_hide_confirm_button(self):
        """
        Compute method to check if the Confirm button should be hidden for the current user.
        """
        for record in self:
            record.hide_confirm_button = bool(
                self.env.user.hide_button_ids.filtered(
                    lambda b: b.model == 'sale.order' and b.button_name == 'action_confirm'
                )
            )

    hide_confirm_button = fields.Boolean(
        string="Hide Confirm Button",
        compute="_compute_hide_confirm_button",
        store=False,
        help="Computed field to hide the Confirm button based on user restrictions."
    )
