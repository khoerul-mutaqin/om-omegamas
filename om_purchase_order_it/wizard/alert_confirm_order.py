from odoo import fields, models, api


class AlertConfirmOrder(models.TransientModel):
    _name = 'alert.confirm.purchase.order'
    _description = 'Alert Confirm Purchase Order'

    purchase_id = fields.Many2one('purchase.order', string='Purchase Order', required=True)

    def button_confirm_manual(self):
        self.ensure_one()
        self.purchase_id._original_button_action_confirm()
        return {'type': 'ir.actions.act_window_close'}