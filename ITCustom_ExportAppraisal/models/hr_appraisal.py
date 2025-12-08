# -*- coding: utf-8 -*-
from odoo import models

class HrAppraisal(models.Model):
    _inherit = 'hr.appraisal'
    
    # Removed the export functionality as we're now using Print
    pass
