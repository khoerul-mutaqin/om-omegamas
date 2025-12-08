from odoo import models, fields, api
from datetime import datetime

class ProductTemplate(models.Model):
    _inherit = 'product.template'
    
    tear_sheet_pdf = fields.Binary(string="Tear Sheet PDF")
    tear_sheet_pdf_filename = fields.Char(string="PDF Filename")
    tear_sheet_pdf_upload_date = fields.Datetime(string="Upload Date :")
    file_pdf = fields.Binary(string="Upload File PDF")
    file_pdf_filename = fields.Char(string="PDF Filename")
    file_pdf_upload_date = fields.Datetime(string="Upload Date :")

    @api.model
    def create(self, vals):
        if vals.get('tear_sheet_pdf'):
            vals['tear_sheet_pdf_upload_date'] = fields.Datetime.now()
        if vals.get('file_pdf'):
            vals['file_pdf_upload_date'] = fields.Datetime.now()
        return super(ProductTemplate, self).create(vals)

    def write(self, vals):
        if 'tear_sheet_pdf' in vals and vals['tear_sheet_pdf']:
            vals['tear_sheet_pdf_upload_date'] = fields.Datetime.now()
        if 'file_pdf' in vals and vals['file_pdf']:
            vals['file_pdf_upload_date'] = fields.Datetime.now()
        return super(ProductTemplate, self).write(vals)
