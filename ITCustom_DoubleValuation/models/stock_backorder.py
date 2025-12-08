from odoo import models, api

class StockBackorderConfirmation(models.TransientModel):
    _inherit = 'stock.backorder.confirmation'
    
    def process(self):
        """Override dengan context management yang benar"""
        # Set context untuk semua related models
        return super(StockBackorderConfirmation, self.with_context(
            creating_backorder=True,
            skip_duplicate_valuation=True
        )).process()
