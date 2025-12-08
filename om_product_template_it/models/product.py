from odoo import fields, models, api, _


class ProductProduct(models.Model):
    _inherit = 'product.product'

    gross_weight = fields.Float(
        string="Gross Weight",
        related='product_tmpl_id.gross_weight',
        store=True,
        readonly=False
    )

    sku = fields.Char(
        string="SKU",
        related='product_tmpl_id.sku',
        store=True,
        readonly=False
    )

    volume_packing = fields.Float(
        string="Volume Packing",
        related='product_tmpl_id.volume_packing',
        store=True,
        readonly=False
    )

    volume_kayu = fields.Float(
        string="Volume Kayu",
        related='product_tmpl_id.volume_kayu',
        store=True,
        readonly=False
    )

    volume_uom_name = fields.Char(
        string='Volume Unit of Measure',
        compute='_compute_volume_uom_name',
        default='m³ CNT'
    )

    volume_packing_uom_name = fields.Char(
        string='Volume Packing Unit of Measure',
        compute='_compute_volume_packing_uom_name',
        default='m³ Packing (sum dari cbm)'
    )

    volume_kayu_uom_name = fields.Char(
        string='Volume Kayu Unit of Measure',
        compute='_compute_volume_kayu_uom_name',
        default='m³ Vlegal'
    )

    def _compute_volume_uom_name(self):
        for record in self:
            record.volume_uom_name = 'm³ CNT'

    def _compute_volume_packing_uom_name(self):
        for record in self:
            record.volume_packing_uom_name = 'm³ Packing'

    def _compute_volume_kayu_uom_name(self):
        for record in self:
            record.volume_kayu_uom_name = 'm³ Vlegal'




class ProductTemplate(models.Model):
    _inherit = 'product.template'

    height = fields.Float(
        string="Height"
    )

    width = fields.Float(
        string="Width"
    )

    depth = fields.Float(
        string="Depth"
    )
    
    sku = fields.Char(
        string="SKU"
    )
    
    hs_code_usa = fields.Char(
        string="HS Code USA"
    )

    gross_weight = fields.Float(
        string="Gross Weight"
    )

    volume_packing = fields.Float(
        string="Volume Packing"
    )

    volume_kayu = fields.Float(
        string="Volume Kayu"
    )

    volume_uom_name = fields.Char(
        string='Volume Unit of Measure',
        compute='_compute_volume_uom_name',
        default='m³ CNT'
    )

    volume_packing_uom_name = fields.Char(
        string='Volume Packing Unit of Measure',
        compute='_compute_volume_packing_uom_name',
        default='m³ Packing'
    )

    volume_kayu_uom_name = fields.Char(
        string='Volume Kayu Unit of Measure',
        compute='_compute_volume_kayu_uom_name',
        default='m³ Vlegal'
    )

    def _compute_volume_uom_name(self):
        for record in self:
            record.volume_uom_name = 'm³ CNT'

    def _compute_volume_packing_uom_name(self):
        for record in self:
            record.volume_packing_uom_name = 'm³ Packing'

    def _compute_volume_kayu_uom_name(self):
        for record in self:
            record.volume_kayu_uom_name = 'm³ Vlegal'

    external_id = fields.One2many(
        'sale.id.external',
        'product',
        string="External ID",
        copy=False,
    )

    def write(self, vals):
        for record in self:
            if 'weight' in vals and record.weight != vals['weight']:
                old_weight = record.weight
                new_weight = vals['weight']
                message = _("Berat produk berubah dari %.2f kg menjadi %.2f kg.") % (old_weight, new_weight)
                record.message_post(body=message)
        return super(ProductTemplate, self).write(vals)


class ProductPackaging(models.Model):
    _inherit = 'product.packaging'

    height = fields.Float(
        string="Height",
        related='package_type_id.height',
        readonly=False
    )

    width = fields.Float(
        string="Width",
        related='package_type_id.width',
        readonly=False
    )

    packaging_length = fields.Float(
        string="Length",
        related='package_type_id.packaging_length',
        readonly=False
    )

    cbm = fields.Float(
        string="CBM",
        compute='_compute_cbm',
        store=True,
        digits=(10, 4)
    )

    @api.depends('height', 'width', 'packaging_length')
    def _compute_cbm(self):
        for record in self:
            # Calculate CBM (cubic meters) from dimensions in cm
            # 1 CBM = 1,000,000 cm³
            record.cbm = (record.height * record.width * record.packaging_length) / 1000000

