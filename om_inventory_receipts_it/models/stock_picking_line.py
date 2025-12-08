from odoo import fields, models, api
import json


class StockPickingLine(models.Model):
    _inherit = 'stock.move'

    # Hubungan ke purchase.order.line
    purchase_line_id = fields.Many2one(
        'purchase.order.line',
        string='Purchase Order Line',
    )

    # Relasi ke departemen berdasarkan purchase.order.line
    depart_per_prod = fields.Many2one(
        'hr.department',
        string="Department Purchase",
        related='purchase_line_id.depart_for_product',
        store=True,
        readonly=False,
    )

    analytic_precision = fields.Integer(default=2)

    analytic_distribution = fields.Json(
        string="Proyek Purchase",
        related='purchase_line_id.analytic_distribution',
        store=True,
        readonly=False,
    )

    analytic_names = fields.Char(compute='_compute_analytic_names', string='Analytic Names')

    def _compute_analytic_names(self):
        for line in self:
            if line.analytic_distribution:
                ids = [int(i) for i in line.analytic_distribution.keys()]
                names = self.env['account.analytic.account'].browse(ids).mapped('name')
                line.analytic_names = ', '.join(names)
            else:
                line.analytic_names = ''


    analytic_distribution_sale = fields.Json(
        string="Proyek Sales",
        related='sale_line_id.analytic_distribution',
        store=True,
        readonly=False,
    )

    analytic_names_sale = fields.Char(compute='_compute_analytic_names_sale', string='Analytic Names')

    info_to_buyer = fields.Text(
        related='sale_line_id.info_to_buyer',
        store=True,
        readonly=False,
    )

    info_to_production = fields.Text(
        related='sale_line_id.info_to_production',
        store=True,
        readonly=False,
    )
    external_id = fields.Many2one(
        related="sale_line_id.external_id",
        string="External ID",
        help="Pilih ID External untuk produk ini",
        store=True,
    )

    def _compute_analytic_names_sale(self):
        for line in self:
            if line.analytic_distribution_sale:
                ids = [int(i) for i in line.analytic_distribution_sale.keys()]
                names = self.env['account.analytic.account'].browse(ids).mapped('name')
                line.analytic_names = ', '.join(names)
            else:
                line.analytic_names = ''

    # # Relasi ke sale.order.line melalui sale_line_id
    # sale_line_id = fields.Many2one(
    #     'sale.order.line',
    #     string='Sales Order Line',
    #     help="Relasi ke Sales Order Line"
    # )
    #
    # Field related untuk mengambil informasi dari sale.order.line
    # info_to_buyer = fields.Text(
    #     string="Info to Buyer",
    #     related='sale_line_id.info_to_buyer',
    #     store=True,
    #     readonly=False,
    #     help="Informasi untuk pembeli yang berasal dari Sales Order Line"
    # )

