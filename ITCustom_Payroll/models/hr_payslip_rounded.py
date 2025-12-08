# -*- coding: utf-8 -*-
from odoo import models, fields, api
import math

class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    def compute_sheet(self):
        res = super(HrPayslip, self).compute_sheet()
        for payslip in self:
            for line in payslip.line_ids:
                line.amount = math.ceil(line.amount) if line.amount % 1 != 0 else line.amount
                line.total = math.ceil(line.total) if line.total % 1 != 0 else line.total
        return res

class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    # Tidak perlu compute field tambahan karena pembulatan sudah dilakukan di compute_sheet
    pass
