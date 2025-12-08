from odoo import models, api

class MrpProduction(models.Model):
    _inherit = 'mrp.production'
    
    def _get_backorder_mo_vals(self):
        """Override untuk set context di backorder MO"""
        vals = super(MrpProduction, self)._get_backorder_mo_vals()
        # Add context untuk mencegah duplicate valuation
        self = self.with_context(creating_backorder=True, skip_valuation=True)
        return vals