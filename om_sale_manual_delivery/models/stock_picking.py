
from odoo import SUPERUSER_ID, _, api, Command, fields, models
from odoo.exceptions import UserError

class StockPicking(models.Model):
    _inherit = 'stock.picking'

    # group_id = fields.Many2one(
    #     'procurement.group', 'Procurement Group',
    #     readonly=False, related='move_ids.group_id', store=True)
    analytic_account_id = fields.Many2one('account.analytic.account', string='Proyek')
    department_id = fields.Many2one('hr.department', string='Department')
    
