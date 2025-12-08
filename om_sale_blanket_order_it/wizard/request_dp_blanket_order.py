from odoo import models, fields, api
from odoo.exceptions import UserError

class RequestDPBlanketOrder(models.TransientModel):
    _name = 'wizard.request.dp.blanket.order'
    _description = 'Wizard Requst DP Blanket Order'

    blanket_order_id = fields.Many2one('sale.blanket.order', string='Blanket Order', required=True)
    dp_type = fields.Selection([
        ('percentage', 'Persentase'),
        ('fixed', 'Fixed Amount')
    ], string='Tipe DP', required=True)
    
    base_on = fields.Selection([
        ('price', 'Price'),
        ('om_price', 'OM Price')
    ], string='Harga Berdasarkan?')

    currency_id = fields.Many2one(
        'res.currency',
        string="Currency",
        related='blanket_order_id.currency_id',
        store=True, 
        readonly=True,
    )
    
    percentage = fields.Float(string='Persentase (%)')
    
    fixed_amount = fields.Monetary(string='Fixed Amount', currency_field='currency_id')

    @api.onchange('dp_type')
    def _onchange_dp_type(self):
        if self.dp_type != 'percentage':
            self.base_on = False
            self.percentage = 0.0
        if self.dp_type != 'fixed':
            self.fixed_amount = 0.0

    def action_confirm_dp(self):
        self.ensure_one()
        if self.base_on == 'price':
            text_base_on = "Price"
        else:
            text_base_on = "OM Price"
        if self.dp_type == 'percentage':
            if not self.base_on or self.percentage <= 0:
                raise UserError("Pilih harga dan isi persentase yang valid.")
            base_amount = self.blanket_order_id.amount_total if self.base_on == 'price' else self.blanket_order_id.amount_total_sec_price
            dp_value = base_amount * (self.percentage / 100)
            ket_request_dp = f"Requested DP {self.percentage}% Based on Total {text_base_on}"
        else:
            if self.fixed_amount <= 0:
                raise UserError("Fixed amount harus lebih dari 0.")
            dp_value = self.fixed_amount
            ket_request_dp = f"Requested DP Fixed Amount {self.fixed_amount}" 
        # Simpan ke field req_dp_amount
        self.blanket_order_id.req_dp_amount = dp_value
        self.blanket_order_id.ket_request_dp = ket_request_dp
        return {'type': 'ir.actions.act_window_close'}
