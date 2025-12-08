from odoo import api, fields, models


class StockReportLine(models.Model):
    _name = 'stock.report.line'
    _description = 'Stock Movement and Value Report Line'
    _order = 'category_id, product_id'

    product_id = fields.Many2one('product.product', string='Product', required=True, readonly=True)
    category_id = fields.Many2one('product.category', string='Category', required=True, readonly=True)
    uom_id = fields.Many2one('uom.uom', string='UoM', required=True, readonly=True)
    
    currency_id = fields.Many2one('res.currency', string='Currency',
        readonly=True, default=lambda self: self.env.company.currency_id)
    
    opening_qty = fields.Float(string='Opening Qty', readonly=True, digits='Product Unit of Measure')
    opening_value = fields.Monetary(string='Opening Value', readonly=True, currency_field='currency_id')
    
    qty_in = fields.Float(string='Quantity In', readonly=True, digits='Product Unit of Measure')
    value_in = fields.Monetary(string='Value In', readonly=True, currency_field='currency_id')
    
    qty_out = fields.Float(string='Quantity Out', readonly=True, digits='Product Unit of Measure')
    value_out = fields.Monetary(string='Value Out', readonly=True, currency_field='currency_id')
    
    closing_qty = fields.Float(string='Closing Qty', readonly=True, digits='Product Unit of Measure')
    closing_value = fields.Monetary(string='Closing Value', readonly=True, currency_field='currency_id')
    
    unit_price = fields.Monetary(string='Unit Price', readonly=True, currency_field='currency_id')
    
    date_from = fields.Date(string="Date From", readonly=True)
    date_to = fields.Date(string="Date To", readonly=True)

    # Computed fields for analysis
    total_movement_qty = fields.Float(string='Total Movement', compute='_compute_movements',
        digits='Product Unit of Measure', store=True,
        help='Total quantity moved (in + out)')
    
    total_movement_value = fields.Monetary(string='Total Movement Value', compute='_compute_movements',
        currency_field='currency_id', store=True,
        help='Total value moved (in + out)')
    
    has_movements = fields.Boolean(string='Has Movements', compute='_compute_movements',
        store=True,
        help='Indicates if the product had any movements during the period')

    @api.depends('qty_in', 'qty_out', 'value_in', 'value_out')
    def _compute_movements(self):
        for record in self:
            record.total_movement_qty = abs(record.qty_in) + abs(record.qty_out)
            record.total_movement_value = abs(record.value_in) + abs(record.value_out)
            record.has_movements = bool(record.qty_in or record.qty_out)

    def init(self):
        """Create indexes for better performance"""
        self._cr.execute("""
            SELECT indexname FROM pg_indexes 
            WHERE indexname = 'stock_report_line_product_category_idx'
        """)
        if not self._cr.fetchone():
            self._cr.execute("""
                CREATE INDEX stock_report_line_product_category_idx 
                ON stock_report_line (category_id, product_id)
            """)

    def name_get(self):
        """Custom name display"""
        return [(record.id, f"{record.product_id.name} ({record.category_id.name})") 
                for record in self]

    @api.model
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        """Override to ensure proper aggregation of monetary fields"""
        result = super().read_group(domain, fields, groupby, offset=offset, 
                                  limit=limit, orderby=orderby, lazy=lazy)
        
        # Ensure monetary fields are properly summed
        monetary_fields = ['opening_value', 'value_in', 'value_out', 
                         'closing_value', 'total_movement_value']
        
        for group in result:
            for field in monetary_fields:
                if field in group:
                    group[field] = float(group[field] or 0)
                    
        return result
    
    def action_open_move_history(self):
        self.ensure_one()
        action = self.env.ref('stock.stock_move_line_action').read()[0] 
        date_start = self.date_from
        date_end = self.date_to
        
        # Set domain to filter by product and date
        action['domain'] = [ '&', ('product_id', '=', self.product_id.id), '|', '|',
            '&', ('accounting_date', '>=', date_start), ('accounting_date', '<=', date_end),
            '&', ('date_inventory', '>=', date_start), ('date_inventory', '<=', date_end),
            '&', ('date_manufacturing', '>=', date_start), ('date_manufacturing', '<=', date_end)
        ]
        
        # Update action name to show which product
        action['name'] = f'Move History: {self.product_id.display_name}'
        
        return action