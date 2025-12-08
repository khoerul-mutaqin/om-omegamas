from odoo import models, api

class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'
    
    @api.model
    def create(self, vals):
        """Prevent duplicate valuation layer creation"""
        # Skip jika dalam context backorder dan ada duplicate
        if self.env.context.get('skip_duplicate_valuation'):
            # Cek untuk existing layer
            existing = self.search([
                ('stock_move_id', '=', vals.get('stock_move_id')),
                ('product_id', '=', vals.get('product_id')),
            ], order='id desc', limit=1)
            
            if existing:
                # Update existing daripada create baru
                existing.write({
                    'quantity': vals.get('quantity', existing.quantity),
                    'value': vals.get('value', existing.value),
                })
                return existing
                
        return super(StockValuationLayer, self).create(vals)
