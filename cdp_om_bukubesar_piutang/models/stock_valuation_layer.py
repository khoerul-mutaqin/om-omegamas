from odoo import api, fields, models, Command, _

class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'
    

    x_in_valuation = fields.Monetary(string='In Valuation', currency_field="currency_id", compute="compute_value")  
    x_out_valuation = fields.Monetary(string='Out Valuation', currency_field="currency_id", compute="compute_value")     
    x_qty_balance = fields.Float(related='quantity', string='Balance')          

    x_qty_in  = fields.Float(string='Qty In', compute="compute_value")           
    x_qty_out = fields.Float(string='Qty Out', compute="compute_value")    
        
    @api.depends('quantity','value')
    def compute_value(self):
        for rec in self:
            balance =  rec.quantity
            value = rec.value
            if balance > 0:
                rec['x_qty_in'] = balance
                rec['x_in_valuation'] = value
                rec['x_qty_out'] = 0
                rec['x_out_valuation'] = 0
            else:
                rec['x_qty_in'] = 0
                rec['x_in_valuation'] = 0
                rec['x_qty_out'] = value
                rec['x_out_valuation'] = balance
                

    x_qty_start = fields.Float(string='Start')        
    x_start_valuation = fields.Monetary(string='Start Valuation', currency_field="currency_id")          
    x_studio_date = fields.Datetime(related="product_id.stock_move_ids.move_line_ids.date", string="Order Date", readonly=False)

    x_studio_description = fields.Text(string="Description", readonly=False)
    x_studio_operation_type = fields.Many2one(
        "stock.picking.type",
        related="product_id.stock_move_ids.picking_type_id",
        string="Operation Type",
        readonly=True,
        store=False,
    )          
    x_studio_product_category = fields.Many2one(
        "product.category",
        related="product_id.categ_id",
        string="Product Category",
        readonly=True,
        store=False,
    )    
    x_studio_reference = fields.Char(related='product_id.stock_move_ids.reference', string='Reference')          
    x_total_valuation = fields.Monetary(related='value', string='Balance Quantity', currency_field="currency_id")          
