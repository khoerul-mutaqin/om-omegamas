from odoo import api, fields, models

class StockLocation(models.Model):
    _inherit = 'stock.location'

    account_in_id = fields.Many2one('account.account', string='Incoming Account')
    account_out_id = fields.Many2one('account.account', string='Outgoing Account')
    