from odoo import api, fields, models
from odoo.exceptions import UserError

class Picking(models.Model):
    _inherit = 'stock.picking'
    
    def cdp_create_report_valuation(self):
        """
        Mengambil referensi Sale Order dari Stock Picking, lalu mengumpulkan
        semua Lot dari stock moves untuk dibuatkan satu record valuation terpusat.
        """
        so = self.sale_id
        if so:
            for rec in self:
                lot_ids = rec.mapped('move_ids_without_package.lot_ids')
                so.cdp_create_report_valuation(lot_ids=lot_ids)
         
    def cdp_open_report_valuation(self):
        """
        Memproses pembuatan data valuation terbaru berdasarkan picking saat ini, 
        lalu membuka view list/form report valuation yang difilter berdasarkan Sale Order terkait.
        """
        so = self.sale_id
        if so:
            # buat atau update dulu report valuation
            self.cdp_create_report_valuation()
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
        else:
            raise UserError("Transfer Tidak memiliki Sale Order")            


class SaleOrder(models.Model):
    _inherit = "sale.order"
    
    cdp_product_wip_id = fields.Many2one(
        "product.product", string="WIP Product", readonly=True, copy=False
    )
    

    def cdp_open_report_valuation(self):
        """
        Membuka view list/form report valuation yang difilter berdasarkan Sale Order terkait.
        """        
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



    def cdp_create_report_valuation(self,lot_ids=None):
        """
        Fungsi ini digunakan untuk membuat satu record valuation yang 
        menampung seluruh Lot terkait produk yang dikonsumsi/dihasilkan.
        Mendukung multi-lot dalam satu record (Many2many).
        """        
        # Asumsikan ini untuk sale Order
        line_field = self.order_line #line at sale order
        cdp_report_valuation_action = self.env['cdp.report.valuation'].sudo()
        cdp_report_valuation_line_action = self.env['cdp.report.valuation.line'].sudo()
        mrp_production_action = self.env['mrp.production'].sudo()
        stock_valuation_layer_mdl = self.env['stock.valuation.layer'].sudo()

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
                    'lot_ids': lot_ids,
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
                target_mos = real_mos.filtered(lambda m: m.lot_producing_id in lot_ids)
                
                for mo in target_mos:
                    # Ambil Lot dari MO ini untuk digunakan di setiap line RM-nya
                    current_lot_id = mo.lot_producing_id.id
                    
                    # Filter RM: exclude WIP products based on category flag
                    valid_rm_moves = mo.move_raw_ids
                    
                    # 4. Cari valuation
                    target_svl =  False
                    domain = [("product_id.categ_id.cdp_for_product_wip", "=", True), ("reference", "=", mo.name)]
                    real_svl = stock_valuation_layer_mdl.search(domain)
                
                    # only create for not wip product             
                    for rm in valid_rm_moves:
                        # hanya wip yang memiliki value consume
                        target_svl = real_svl if rm.product_id.categ_id.cdp_for_product_wip else False
                        mo_line_values.append({
                            'order_id': master_valuation.id,
                            'name': rm.product_id.display_name,
                            'product_id': rm.product_id.id,
                            'lot_producing_id': current_lot_id,
                            # 'product_uom_qty': rm.product_uom_qty,  # sebelumnya ambil dari rm product_uom_qty 
                            # 'price_unit': rm.product_uom_qty,  # sebelumnya ambil dari rm price_unit 
                            'product_uom_qty': target_svl.quantity if target_svl else rm.product_uom_qty,  # ambil dari valuation jadi hanya product wip nya yang kepakai berapa
                            'price_unit': target_svl.value if target_svl else rm.price_unit,  # ambil dari valuation jadi hanya product wip nya yang kepakai berapa
                            'company_id': rm.company_id.id,
                            'currency_id': rm.company_id.currency_id.id,
                        })          

                # 4. Create baris baru (setelah yang lama dihapus di atas jika prosesnya Update)
                if mo_line_values:
                    cdp_report_valuation_line_action.create(mo_line_values)

                # 5. calculate product_uom_qty and price
                master_valuation.cdp_calculate_qty_value()

class CdpReportValuation(models.Model):
    _name = "cdp.report.valuation"
    _inherit = ['analytic.mixin']
    _description = "Cdp Report Valuation"
    _rec_name = 'product_id'

    def cdp_calculate_qty_value(self):
        """
        Menghitung total kuantitas dan total harga unit dari seluruh 
        baris detail (line_ids) untuk dimasukkan ke dalam header valuation.
        Fungsi ini mendukung kalkulasi massal untuk banyak record sekaligus.
        """
        for rec in self:
            total_qty = 0.0
            total_price = 0.0
            
            for line in rec.line_ids:
                total_qty += line.product_uom_qty
                total_price += line.price_unit
            
            # Update field pada record terkait
            rec.update({
                'product_uom_qty': total_qty,
                'price_unit': total_price,
            })     
    
    name = fields.Char(string='Name', required=True)
    
    # Relationship to Child Lines
    line_ids = fields.One2many(
        'cdp.report.valuation.line', 'order_id', 
        string="Valuation Lines"
    )
    
    lot_ids = fields.Many2many(
        'stock.lot', 
        'cdp_report_valuation_stock_lot_rel', # Explicit relation table name
        'report_id',                          # Column 1
        'lot_id',                             # Column 2
        string="Lots"
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
        "product.product", string="Product"
    )
    product_uom_qty = fields.Float(string="Quantity", default=0.0)
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
    lot_producing_id = fields.Many2one('stock.lot', string="Lot ID")
    product_id = fields.Many2one('product.product', string="Product")
    product_uom_qty = fields.Float(string="Quantity", default=0.0)
    price_unit = fields.Float(string="Unit Price", default=0.0)
    company_id = fields.Many2one(related='order_id.company_id', store=True)
    currency_id = fields.Many2one(related='order_id.currency_id', store=True)
    