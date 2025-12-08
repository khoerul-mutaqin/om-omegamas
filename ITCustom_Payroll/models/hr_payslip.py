from odoo import models, fields

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    state = fields.Selection([
        ('draft', 'Draft'),
        ('verify', 'Waiting'),
        ('check', 'Check'),
        ('done', 'Done'),
        ('paid', 'Paid'),
        ('cancel', 'Canceled'),
    ], string='Status', readonly=True, copy=False, tracking=True, default='draft')

    def action_check(self):
        for payslip in self:
            payslip.state = 'check'
        return {}