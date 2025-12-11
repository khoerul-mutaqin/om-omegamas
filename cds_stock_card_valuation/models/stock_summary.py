from odoo import fields, models, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)


class StockSummary(models.Model):
    _inherit = "fal.stock.summary"

    def update_valuation(self):
        for summary in self:
            locations = self.env['stock.location'].sudo().search(
                [('id', 'child_of', summary.location_id.id)]
            ).ids

            if not locations or not summary.line_ids:
                continue

            tuple_location = tuple(locations)
            date_start = fields.Datetime.to_string(summary.date_start)
            date_end = fields.Datetime.to_string(summary.date_end)
            cr = self.env.cr

            # Ambil semua product_id yang relevan
            product_ids = tuple(summary.line_ids.mapped('product_id').ids)

            if not product_ids:
                continue

            # Buat 1 query besar untuk semua produk
            query = f"""
                SELECT
                    svl.product_id,
                    SUM(
                        CASE 
                            WHEN svl.create_date <= %s
                                 AND sm.location_dest_id IN %s
                            THEN svl.value ELSE 0 END
                    ) AS start_in,
                    SUM(
                        CASE 
                            WHEN svl.create_date <= %s
                                 AND sm.location_id IN %s
                            THEN svl.value ELSE 0 END
                    ) AS start_out,
                    SUM(
                        CASE 
                            WHEN svl.create_date BETWEEN %s AND %s
                                 AND sm.location_dest_id IN %s
                            THEN svl.value ELSE 0 END
                    ) AS in_val,
                    SUM(
                        CASE 
                            WHEN svl.create_date BETWEEN %s AND %s
                                 AND sm.location_id IN %s
                            THEN svl.value ELSE 0 END
                    ) AS out_val
                FROM stock_valuation_layer svl
                JOIN stock_move sm ON sm.id = svl.stock_move_id
                WHERE svl.product_id IN %s
                GROUP BY svl.product_id
            """

            params = (
                date_start, tuple_location,  # start_in
                date_start, tuple_location,  # start_out
                date_start, date_end, tuple_location,  # in_val
                date_start, date_end, tuple_location,  # out_val
                product_ids,
            )

            cr.execute(query, params)
            results = cr.fetchall()

            # Convert hasil ke dict {product_id: values}
            valuation_map = {
                r[0]: {
                    'start_valuation': (r[1] or 0.0) + (r[2] or 0.0),
                    'in_valuation': r[3] or 0.0,
                    'out_valuation': r[4] or 0.0,
                    'total_valuation': (r[1] or 0.0) + (r[2] or 0.0) + (r[3] or 0.0) + (r[4] or 0.0),
                }
                for r in results
            }

            # Apply hasil ke tiap line
            for line in summary.line_ids:
                val = valuation_map.get(line.product_id.id, {})
                if val:
                    line.write(val)

    def action_calculate(self):
        res = super(StockSummary, self).action_calculate()
        self.sudo().update_valuation()
        # Sync lines for missing products
        self.sudo().cdp_sync_stock_summary_lines_for_missing_products()
        # Set initial valuation from previous summary
        self.sudo().cdp_set_initial_valuation_from_previous()
        return res

    def cdp_set_initial_valuation_from_previous(self):
        # For each summary, find the previous summary and map valuations
        array = []
        for summary in self:
            domain = [
                ("location_id", "=", summary.location_id.id),
                ("date_start", "<", summary.date_start)
            ]
            # Get the latest previous summary
            previous_summary = summary.env[summary._name].search(
                domain,
                limit=1
            )
            # if found, map product valuations
            if previous_summary:
                valuation_map = {
                    line.product_id.id: (line.total_valuation)
                    for line in previous_summary.line_ids
                }
                # Assign values to current summary lines
                for smr_line in summary.line_ids:
                    product_id = smr_line.product_id.id
                    # Avoid duplicate assignment
                    if product_id not in array:
                        array.append(smr_line.product_id.id)
                        value_to_assign = valuation_map.get(product_id, 0.0)
                        # Assign the value
                        smr_line['cdp_start_valuation'] = value_to_assign
    
    def cdp_sync_stock_summary_lines_for_missing_products(self):
        master_data = self.env[self._name].search([])
        bigger_array = []
        current_array = []
        for record in self:
            # Find the most big product array from all master data
            most_big_product = -1 
            for master in master_data:
                # Get product ids from master record
                product_ids = master.line_ids.mapped('product_id').ids
                sum_product = len(product_ids)
                # and assign to bigger_array
                if sum_product > most_big_product:
                    most_big_product = sum_product
                    # Assign the biggest array
                    bigger_array = master.line_ids.mapped('product_id').ids
            for summary in record:
                # Get current product ids
                current_array = summary.line_ids.mapped('product_id').ids
            for product_id_to_check in bigger_array:                
                # If product not in current array, create new line
                if product_id_to_check not in current_array:
                    # 1. Browse the product record
                    product_record = self.env['product.product'].browse(product_id_to_check) 
                    if product_record: 
                        # 2. Create new line with 0 values                   
                        new_record = self.env['fal.stock.summary.line'].create({
                            'stock_summary_id': record.id,
                            'product_id': product_record.id,
                            'start_valuation':0.0,
                            'in_valuation': 0.0,
                            'out_valuation': 0.0,
                            'total_valuation': 0.0,
                        })

class StockSummaryLine(models.Model):
    _inherit = "fal.stock.summary.line"
    
    cdp_start_valuation = fields.Float(
        string="Start Valuation Before",
    )
    
    currency_id = fields.Many2one(
        'res.currency',
        string='Currency',
        default=lambda self: self.env.company.currency_id.id,
    )
    start_valuation = fields.Monetary(
        string="Start Valuation",
        currency_field="currency_id",
    )
    in_valuation = fields.Monetary(
        string="In Valuation",
        currency_field="currency_id",
    )
    out_valuation = fields.Monetary(
        string="Out Valuation",
        currency_field="currency_id",
    )
    total_valuation = fields.Monetary(
        string="Balance Valuation",
        currency_field="currency_id",
    )
