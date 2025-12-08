from odoo import fields, models, api


class AccountMoveLine(models.Model):
    _inherit = 'account.move.line'
    _description = 'Add Field Department to Vendors Bill'

    # Hubungan ke purchase.order.line
    purchase_line_id = fields.Many2one(
        'purchase.order.line',
        string='Purchase Order Line',
        store=True
    )

    # Relasi ke departemen berdasarkan purchase.order.line didalam Invoice Line Vendor Bill
    depart_per_prod_pi = fields.Many2one(
        'hr.department',
        string="Department",
        help="Department in Vendor Bill Invoice Line.",
        related='purchase_order_id.order_line.depart_for_product',
        store=True,
        readonly=True,
    )

    analytic_precision = fields.Integer(default=2)

    # Relasi ke analytic_distribution berdasarkan purchase.order.line (PI)
    analytic_distribution_pi = fields.Json(
        string="Proyek",
        help="Analytic Distribution in Vendor Bill Invoice Line.",
        related='purchase_order_id.order_line.analytic_distribution',
        store=True,
        readonly=True,
    )

    analytic_names_pi = fields.Char(compute='_compute_analytic_names_pi', string='Analytic Names')

    def _compute_analytic_names_pi(self):
        for line in self:
            if line.analytic_distribution_pi:
                ids = [int(i) for i in line.analytic_distribution_pi.keys()]
                names = self.env['account.analytic.account'].browse(ids).mapped('name')
                line.analytic_names = ', '.join(names)
            else:
                line.analytic_names = ''

    # Relasi ke departemen berdasarkan Inventory Receipt (TTB)
    depart_per_prod_ttb = fields.Many2one(
        'hr.department',
        string="Department",
        help="Department in Journal Items",
        related='move_id.stock_valuation_layer_ids.stock_move_id.depart_per_prod',
        store=True,
        readonly=False
    )

    analytic_distribution_ttb = fields.Json(
        string="Proyek",
        help="Analytic Distribution in Journal Items",
        related='move_id.stock_valuation_layer_ids.stock_move_id.analytic_distribution',
        store=True,
        readonly=True,
    )

    analytic_names_ttb = fields.Char(compute='_compute_analytic_names_ttb', string='Analytic Names')

    def _compute_analytic_names_ttb(self):
        for line in self:
            if line.analytic_distribution_ttb:
                ids = [int(i) for i in line.analytic_distribution_ttb.keys()]
                names = self.env['account.analytic.account'].browse(ids).mapped('name')
                line.analytic_names = ', '.join(names)
            else:
                line.analytic_names = ''

    analytic_distribution_sale = fields.Json(
        string="Proyek Sale",
        help="Analytic Distribution in Journal Items",
        related='move_id.stock_valuation_layer_ids.stock_move_id.analytic_distribution_sale',
        store=True,
        readonly=True,
    )

    analytic_names_sale = fields.Char(compute='_compute_analytic_names_sale', string='Analytic Names')

    def _compute_analytic_names_sale(self):
        for line in self:
            if line.analytic_distribution_sale:
                ids = [int(i) for i in line.analytic_distribution_sale.keys()]
                names = self.env['account.analytic.account'].browse(ids).mapped('name')
                line.analytic_names = ', '.join(names)
            else:
                line.analytic_names = ''
