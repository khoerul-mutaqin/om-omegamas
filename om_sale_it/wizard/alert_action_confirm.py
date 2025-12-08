from odoo import fields, models, api


class AlertActionConfirm(models.TransientModel):
    _name = 'sale.order.alert.action.confirm'
    _description = 'Alert Confirmation'

    production_id = fields.Many2one('sale.order', string='Sale Order', required=True)

    def action_confirm(self):
        self.ensure_one()
        self.production_id._original_button_action_confirm()
        return {'type': 'ir.actions.act_window_close'}
