from odoo import fields, models, api


class StockValuationLayer(models.Model):
    _inherit = 'stock.valuation.layer'

    depart_per_stock_move_for_valuation = fields.Many2one(
        'hr.department',
        string="Department",
        related='stock_move_id.depart_per_prod',
        store=True,
        readonly=True
    )

    analytic_precision = fields.Integer(default=2)

    analytic_per_stock_move_for_valuation = fields.Json(
        string="Proyek",
        related='stock_move_id.analytic_distribution',
        store=True,
        readonly=True,
    )

    note_per_stock_move_for_valuation = fields.Html(
        string="Note",
        related="stock_move_id.picking_id.note",
        store=True,
        readonly=True,
    )

    depart_per_mrp_production = fields.Many2one(
        'hr.department',
        string='Department Manufacturing',
        related='stock_move_id.production_id.department_id',
        store=True,
        readonly=True,
    )

    analytic_per_mrp_production = fields.Many2one(
        string="Proyek Manufacturing",
        related="stock_move_id.production_id.analytic_account_id",
        store=True,
        readonly=True,
    )

    note_per_mrp_production = fields.Text(
        string="Note Manufacturing",
        related="stock_move_id.production_id.log_note",
        store=True,
        readonly=True,
    )

    accounting_date = fields.Date(
        string="Accounting Date", 
        readonly=True
    )

    date_inventory = fields.Datetime(
        string='Date Inventory',
        related='stock_move_id.picking_id.scheduled_date', 
        readonly=True,   
    )

    date_manufacturing = fields.Datetime(
        string='Date Manufacturing',
        compute='_compute_date_manufacturing',
        store=True,
    )

    @api.depends('stock_move_id.production_id.date_start', 'stock_move_id.raw_material_production_id.date_start')
    def _compute_date_manufacturing(self):
        for record in self:
            if record.stock_move_id.production_id:
                record.date_manufacturing = record.stock_move_id.production_id.date_start
            elif record.stock_move_id.raw_material_production_id:
                record.date_manufacturing = record.stock_move_id.raw_material_production_id.date_start
            else:
                record.date_manufacturing = False

    def create(self, vals_list):
        records = super().create(vals_list)

        for svl in records:
            # Cari quant yang sesuai
            quant = self.env['stock.quant'].search([
                ('product_id', '=', svl.product_id.id),
                ('location_id', '=', svl.stock_move_id.location_dest_id.id),
                ('inventory_quantity_set', '=', True),
            ], limit=1, order='in_date desc')

            if quant and quant.accounting_date:
                svl.accounting_date = quant.accounting_date

        return records
