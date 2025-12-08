from odoo import models, api
from odoo.tools import float_compare

class StockMove(models.Model):
    _inherit = 'stock.move'
    
    def _action_done(self, cancel_backorder=False):
        """Override untuk mencegah valuasi berlebihan saat backorder"""
        # Jika dalam konteks create backorder, handle secara khusus
        if self.env.context.get('creating_backorder'):
            return self._process_backorder_moves(cancel_backorder)
        return super(StockMove, self)._action_done(cancel_backorder=cancel_backorder)
    
    def _process_backorder_moves(self, cancel_backorder=False):
        """Custom logic untuk backorder scenario"""
        # Filter moves yang perlu diproses
        moves_to_process = self.filtered(
            lambda m: m.state not in ['done', 'cancel'] and 
            float_compare(m.quantity, 0, precision_rounding=m.product_uom.rounding) > 0
        )
        
        if not moves_to_process:
            return self
            
        # Untuk manufacturing moves, handle secara khusus
        manufacturing_moves = moves_to_process.filtered(
            lambda m: m.raw_material_production_id or m.production_id
        )
        
        if manufacturing_moves:
            return self._process_manufacturing_backorder(manufacturing_moves, cancel_backorder)
        
        # Untuk non-manufacturing, process seperti biasa
        return super(StockMove, moves_to_process)._action_done(cancel_backorder=cancel_backorder)
    
    def _process_manufacturing_backorder(self, moves, cancel_backorder=False):
        """Special handling untuk manufacturing backorder"""
        result = self.env['stock.move']
        
        for move in moves:
            # Skip jika sudah done
            if move.state in ['done', 'cancel']:
                continue
                
            # Process move dengan context untuk skip duplicate valuation
            super(StockMove, move.with_context(
                skip_duplicate_valuation=True,
                creating_backorder=True
            ))._action_done(cancel_backorder=cancel_backorder)
            
            result |= move
            
        return result
