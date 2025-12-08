from odoo import fields, models, api


class StockMoveLineList(models.Model):
    _inherit = 'stock.move.line'


    depart_for_stock_move = fields.Many2one(
        'hr.department',
        string="Department",
        related='move_id.depart_per_prod',
        store=True,
        readonly=True
    )

    analytic_precision = fields.Integer(default=2)

    analytic_for_stock_move = fields.Json(
        string="Proyek",
        related='move_id.analytic_distribution',
        store=True,
        readonly=True,
    )

    note_per_stock_move_for_stock_move = fields.Html(
        string="Note",
        related="move_id.picking_id.note",
        store=True,
        readonly=True,
    )

    depart_mrp_production_for_stock_move = fields.Many2one(
        'hr.department',
        string='Department Manufacturing',
        related='move_id.production_id.department_id',
        store=True,
        readonly=True,
    )

    analytic_mrp_production_for_stock_move = fields.Many2one(
        string="Proyek Manufacturing",
        related="move_id.production_id.analytic_account_id",
        store=True,
        readonly=True,
    )

    note_mrp_production_for_stock_move = fields.Text(
        string="Note Manufacturing",
        related="move_id.production_id.log_note",
        store=True,
        readonly=True,
    )

    has_out_history = fields.Boolean(string="Has Out History", compute="_compute_has_out_history", store=True)

    accounting_date = fields.Date(string="Accounting Date", compute="_compute_accounting_date", store=True)

    def _compute_accounting_date(self):
        for line in self:
            svl = self.env['stock.valuation.layer'].search([
                ('stock_move_id', '=', line.move_id.id),
                ('product_id', '=', line.product_id.id)
            ], limit=1, order='create_date desc')  # atau order by id desc

            line.accounting_date = svl.accounting_date if svl else False

    date_inventory = fields.Datetime(
        string='Date Inventory',
        related='move_id.picking_id.scheduled_date', 
        readonly=True,   
    )
    date_manufacturing = fields.Datetime(
        'Date Manufacturing',
        compute='_compute_date_manufacturing',
        store=True,
    )

    @api.depends('move_id.production_id.date_start', 'move_id.raw_material_production_id.date_start')
    def _compute_date_manufacturing(self):
        for record in self:
            if record.move_id.production_id:
                record.date_manufacturing = record.move_id.production_id.date_start
            elif record.move_id.raw_material_production_id:
                record.date_manufacturing = record.move_id.raw_material_production_id.date_start
            else:
                record.date_manufacturing = False
                
    @api.depends('product_id')
    def _compute_has_out_history(self):
        for move in self:
            # Cek apakah ada move keluar untuk product ini
            domain = [
                ('product_id', '=', move.product_id.id),
                ('location_id.usage', 'in', ['internal', 'transit']),
                ('location_dest_id.usage', 'not in', ['internal', 'transit']),
                ('state', '=', 'done')  # Opsional, hanya yang sudah selesai
            ]
            exists = self.search_count(domain) > 0
            move.has_out_history = exists

