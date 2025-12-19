from odoo import api, fields, models

class Picking(models.Model):
    _inherit = 'stock.picking'
    
    def cdp_create_report_valuation(self):
        """Ambil sale.order dari production_ids di picking"""
        so = self.sale_id
        if so:
            so.cdp_create_report_valuation()

    def cdp_open_report_valuation(self):            
        """Ambil sale.order dari production_ids di picking"""
        so = self.sale_id
        if so:
            line_id = self.mapped('sale_id.order_line.id')
            model = 'cdp.report.valuation'
            domain = [('name', '=', line_id)]            
            return {
                'name': 'Report Valuation',
                'type': 'ir.actions.act_window',
                'res_model': model,
                'view_mode': 'list,form',
                'target': 'current',
                'domain': domain,
                'context': {
                    'search_default_group_by_product_id': 1,
                    'expand': 1
                },
            }


class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    cdp_product_wip_id = fields.Many2one(
        "product.product", string="WIP Product", readonly=True, copy=False
    )
    

    def cdp_open_report_valuation(self):
        line_id = self.mapped('order_line.id')
        model = 'cdp.report.valuation'
        domain = [('name', '=', line_id)]
        if model:
            return {
                'name': 'Report Valuation',
                'type': 'ir.actions.act_window',
                'res_model': model,
                'view_mode': 'list,form',
                'target': 'current',
                'domain': domain,
                'context': {
                    'search_default_group_by_product_id': 1,
                    'expand': 1
                },
            }

        else:
            raise UserError("Transfer Tidak memiliki Sale Order")


    def cdp_create_report_valuation_line(self):
        for record in self:
            # 1. Ambil semua MO asli
            domain = [('id', 'in', record.mrp_production_ids.ids), ('cdp_is_shadow_mo', '=', False)]
            real_mos = mrp_production_action.search(domain)

            # 2. Loop setiap baris Sale Order (FG)
            for line in record.order_line:
                # --- PINDAHKAN CREATE MASTER KE SINI (DI LUAR LOOP RM) ---
                # Ini memastikan 1 baris SO hanya jadi 1 Master Valuation
                vals = {
                    'name': f"{line.id}",
                    'product_id': line.product_id.id,
                    'company_id': record.company_id.id,
                    'product_uom_qty': line.product_uom_qty, # Tambahkan qty SO
                    'price_unit': line.price_unit,           # Tambahkan harga SO
                }
                master_valuation = cdp_report_valuation_action.create(vals)
                
                mo_line_values = []
                
                # 3. Cari Raw Material (RM) untuk produk ini
                target_mos = real_mos.filtered(lambda m: m.product_id == line.product_id)
                
                # Gunakan dictionary untuk grouping RM agar tidak duplikat di lines
                rm_summary = {}
                
                for rm in target_mos.move_raw_ids:
                    rm_id = rm.product_id.id
                    if rm_id not in rm_summary:
                        rm_summary[rm_id] = {
                            'order_id': master_valuation.id,
                            'name': rm.product_id.display_name,
                            'product_id': rm_id,
                            'product_uom_qty': 0.0,
                            'company_id': rm.company_id.id,
                            'currency_id': rm.company_id.currency_id.id,
                        }
                    # Jumlahkan qty RM jika ada bahan yang sama dari beberapa MO
                    rm_summary[rm_id]['product_uom_qty'] += rm.product_uom_qty

                # 4. Create semua baris RM sekaligus untuk Master ini
                if rm_summary:
                    cdp_report_valuation_line_action.create(list(rm_summary.values()))

    def cdp_create_report_valuation(self):
        # Asumsikan ini untuk sale Order
        line_field = self.order_line #line at sale order
        cdp_report_valuation_action = self.env['cdp.report.valuation'].sudo()
        cdp_report_valuation_line_action = self.env['cdp.report.valuation.line'].sudo()
        mrp_production_action = self.env['mrp.production'].sudo()

        # Assuming 'self' is a recordset of Sale Orders
        # Pastikan cdp_report_valuation_action adalah model yang benar (Master)
        # Pastikan cdp_report_valuation_line_action adalah model baris (Line)
        for record in self:
            # 1. Ambil semua MO asli (bukan shadow)
            domain = [('id', 'in', record.mrp_production_ids.ids), ('cdp_is_shadow_mo', '=', False)]
            real_mos = mrp_production_action.search(domain)

            # 2. Loop setiap baris Sale Order (FG)
            for line in record.order_line:
                # CEK APAKAH SUDAH ADA: Cari master berdasarkan kriteria unik
                # Contoh: berdasarkan nama dan produk yang sama
                master_valuation = cdp_report_valuation_action.search([
                    ('product_id', '=', line.product_id.id),
                    ('company_id', '=', record.company_id.id),
                    ('name', '=', line.id)
                ], limit=1)

                vals = {
                    'name': f"{line.id}",
                    'product_id': line.product_id.id,
                    'company_id': record.company_id.id,
                }

                if master_valuation:
                    # UPDATE: Jika sudah ada, update master
                    master_valuation.write(vals)
                    # Hapus baris lama agar tidak double saat di-create ulang di Step 4
                    master_valuation.line_ids.unlink() 
                else:
                    # CREATE: Jika belum ada, buat baru
                    master_valuation = cdp_report_valuation_action.create(vals)
                
                mo_line_values = []

                # 3. Cari Raw Material (RM) yang HANYA untuk FG ini
                target_mos = real_mos.filtered(lambda m: m.product_id == line.product_id)
                
                for rm in target_mos.move_raw_ids:
                    mo_line_values.append({
                        'order_id': master_valuation.id,
                        'name': rm.product_id.display_name,
                        'product_id': rm.product_id.id,
                        'product_uom_qty': rm.product_uom_qty,
                        'company_id': rm.company_id.id,
                        'currency_id': rm.company_id.currency_id.id,
                    })

                # 4. Create baris baru (setelah yang lama dihapus di atas jika prosesnya Update)
                if mo_line_values:
                    cdp_report_valuation_line_action.create(mo_line_values)


class CdpReportValuation(models.Model):
    _name = "cdp.report.valuation"
    _inherit = ['analytic.mixin']
    _description = "Cdp Report Valuation"

    
    name = fields.Char(string='Name', required=True)
    
    # Relationship to Child Lines
    line_ids = fields.One2many(
        'cdp.report.valuation.line', 'order_id', 
        string="Valuation Lines"
    )

    company_id = fields.Many2one(
        "res.company", string="Company",
        default=lambda self: self.env.company,
        required=True,
    )
    currency_id = fields.Many2one(
        "res.currency", string="Currency",
        related='company_id.currency_id', # Simplified
        readonly=True,
    )
    
    product_id = fields.Many2one(
        "product.product", string="WIP Product"
    )
    product_uom_qty = fields.Float(string="Quantity", default=1.0)
    price_unit = fields.Float(string="Unit Price", default=0.0)

class CdpReportValuationLine(models.Model):            
    _name = 'cdp.report.valuation.line'
    _inherit = ['analytic.mixin']
    _description = "Cdp Report Valuation Line"

    order_id = fields.Many2one(
        'cdp.report.valuation', string="Parent Reference", 
        required=True, ondelete='cascade'
    )
    sequence = fields.Integer(default=10)
    name = fields.Char(string='Description', required=True)

    product_id = fields.Many2one('product.product', string="Product")
    
    # Use 'uom.category' as the comodel to fix the KeyError
    product_uom_category_id = fields.Many2one(
        'uom.category',
        related='product_id.uom_id.category_id', 
        string="UoM Category",
        readonly=True
    )

    product_uom = fields.Many2one(
        'uom.uom', string="Unit of Measure",
        domain="[('category_id', '=', product_uom_category_id)]"
    )

    product_uom_qty = fields.Float(string="Quantity", default=1.0)
    price_unit = fields.Float(string="Unit Price", default=0.0)

    company_id = fields.Many2one(related='order_id.company_id', store=True)
    currency_id = fields.Many2one(related='order_id.currency_id', store=True)