# -*- coding: utf-8 -*-

from odoo import models, fields, api


class StockMove(models.Model):
    _inherit = 'stock.move'

    def _generate_valuation_lines_data(self, partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, svl_id, description):
        self.ensure_one()

        # Panggil fungsi original
        rslt = super()._generate_valuation_lines_data(
            partner_id, qty, debit_value, credit_value, debit_account_id, credit_account_id, svl_id, description
        )

        # Tentukan analytic_distribution jika kondisi terpenuhi
        analytic_distribution = {}
        if self.raw_material_production_id and self.raw_material_production_id.analytic_account_id:
        # if self.raw_material_production_id and self.raw_material_production_id.project_id and self.raw_material_production_id.project_id.account_id:
            analytic_distribution = {str(self.raw_material_production_id.analytic_account_id.id): 100}
            

        # Update analytic_distribution hanya jika belum ada
        if analytic_distribution:
            if not rslt['credit_line_vals'].get('analytic_distribution'):
                rslt['credit_line_vals']['analytic_distribution'] = analytic_distribution
            if not rslt['debit_line_vals'].get('analytic_distribution'):
                rslt['debit_line_vals']['analytic_distribution'] = analytic_distribution

        return rslt