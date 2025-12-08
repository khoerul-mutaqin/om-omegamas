from odoo import models, api
import os
import re

class DocumentsDocument(models.Model):
    _inherit = 'documents.document'

    @api.model
    def create(self, vals):
        if vals.get('name'):
            name = vals['name']
            base, ext = os.path.splitext(name)
            # Search for existing names that start with base and end with ext, including suffixes like (number)
            pattern = f'^{re.escape(base)}(\\(\\d+\\))?{re.escape(ext)}$'
            existing_records = self.search([('name', 'ilike', base + '%')])
            suffixes = []
            for record in existing_records:
                if re.match(pattern, record.name, re.IGNORECASE):
                    # Extract suffix number if present
                    match = re.search(r'\((\d+)\)', record.name)
                    if match:
                        suffixes.append(int(match.group(1)))
                    else:
                        suffixes.append(0)
            if suffixes:
                max_suffix = max(suffixes)
                new_suffix = max_suffix + 1
                vals['name'] = f"{base}({new_suffix}){ext}"
            else:
                vals['name'] = name
        return super().create(vals)

class IrAttachment(models.Model):
    _inherit = 'ir.attachment'

    @api.model
    def create(self, vals):
        if vals.get('name'):
            name = vals['name']
            base, ext = os.path.splitext(name)
            pattern = f'^{re.escape(base)}(\\(\\d+\\))?{re.escape(ext)}$'
            existing_records = self.search([('name', 'ilike', base + '%')])
            suffixes = []
            for record in existing_records:
                if re.match(pattern, record.name, re.IGNORECASE):
                    match = re.search(r'\((\d+)\)', record.name)
                    if match:
                        suffixes.append(int(match.group(1)))
                    else:
                        suffixes.append(0)
            if suffixes:
                max_suffix = max(suffixes)
                new_suffix = max_suffix + 1
                vals['name'] = f"{base}({new_suffix}){ext}"
            else:
                vals['name'] = name
        return super().create(vals)
