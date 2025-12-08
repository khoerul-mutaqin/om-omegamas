from odoo import fields, models


class PurchaseOrderLine(models.Model):
    _inherit = 'purchase.order.line'

    purchase_request_line_id = fields.Many2one(
        'purchase.request.line',
        string="Purchase Request Line"
    )

    depart_for_product = fields.Many2one(
        'hr.department',
        string="Department",
        related='purchase_request_lines.department_id',
        store=True,
        readonly=True
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

    def _prepare_stock_move_vals(self, picking, price_unit, product_uom_qty, product_uom):
        vals = super()._prepare_stock_move_vals(picking, price_unit, product_uom_qty, product_uom)
        vals['purchase_line_id'] = self.id  # Pastikan relasi terisi
        return vals


class PurchaseRequestLine(models.Model):
    _inherit = "purchase.request.line"

    analytic_names = fields.Char(compute='_compute_analytic_names', string='Analytic Names')

    def _compute_analytic_names(self):
        for line in self:
            if line.analytic_distribution:
                ids = [int(i) for i in line.analytic_distribution.keys()]
                names = self.env['account.analytic.account'].browse(ids).mapped('name')
                line.analytic_names = ', '.join(names)
            else:
                line.analytic_names = ''

