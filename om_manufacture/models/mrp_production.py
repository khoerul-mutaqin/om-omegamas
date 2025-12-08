# -*- coding: utf-8 -*-

from odoo import models, fields, api


class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    # _inherit = ["mrp.production", "analytic.mixin"]

    # analytic_distribution = fields.Json(string='Proyek')
    analytic_account_id = fields.Many2one('account.analytic.account', string='Proyek')
    department_id = fields.Many2one('hr.department', string='Department')