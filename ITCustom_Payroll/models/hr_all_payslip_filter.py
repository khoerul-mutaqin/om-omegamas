# models/hr_payslip.py

from odoo import models, fields, api

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'
    
    @api.model
    def _get_default_filter(self):
        return [('state', '=', 'verify')]
    
    @api.model
    def search(self, args, offset=0, limit=None, order=None, count=False):
        if not args and self._context.get('apply_default_filter', True):
            args = self._get_default_filter()
        return super(HrPayslip, self).search(args, offset=offset, limit=limit, order=order, count=count)