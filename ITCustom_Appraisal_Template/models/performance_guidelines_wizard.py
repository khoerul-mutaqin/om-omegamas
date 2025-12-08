from odoo import models, fields, api

class PerformanceGuidelinesWizard(models.TransientModel):
    _name = 'performance.guidelines.wizard'
    _description = 'Performance Guidelines Wizard'
    
    appraisal_id = fields.Many2one('hr.appraisal', string='Appraisal', required=True)
    performance_guidelines_umum_html = fields.Html(
        string="Pedoman Penilaian Perilaku Kerja",
        compute="_compute_guidelines_html"
    )
    performance_guidelines_khusus_html = fields.Html(
        string="Pedoman Penilaian Hasil Kerja",
        compute="_compute_guidelines_html"
    )
    performance_guidelines_kepemimpinan_html = fields.Html(
        string="Pedoman Penilaian Kepemimpinan",
        compute="_compute_guidelines_html"
    )
    
    @api.depends('appraisal_id')
    def _compute_guidelines_html(self):
        for wizard in self:
            if wizard.appraisal_id and wizard.appraisal_id.department_id:
                # Determine the correct template based on employee role
                is_atasan = wizard.appraisal_id.memiliki_bawahan
                
                # Find the specific template that matches department and role
                template = self.env['appraisal.template'].search([
                    ('department_id', '=', wizard.appraisal_id.department_id.id),
                    ('atasan', '=', is_atasan)
                ], limit=1)
                
                # If no specific template found, try without role filter
                if not template:
                    template = self.env['appraisal.template'].search([
                        ('department_id', '=', wizard.appraisal_id.department_id.id)
                    ], limit=1)
                
                # Collect guidelines from the specific template
                umum_guidelines = template.performance_guidelines_umum if template else []
                khusus_guidelines = template.performance_guidelines_khusus if template else []
                
                # Only collect kepemimpinan guidelines if employee is a manager/atasan
                kepemimpinan_guidelines = []
                if template and is_atasan:
                    kepemimpinan_guidelines = template.performance_guidelines_kepemimpinan
                
                # Generate HTML for Umum guidelines
                if umum_guidelines:
                    umum_html = self._generate_guidelines_html(umum_guidelines, "Umum")
                    wizard.performance_guidelines_umum_html = umum_html
                else:
                    wizard.performance_guidelines_umum_html = False
                
                # Generate HTML for Khusus guidelines
                if khusus_guidelines:
                    khusus_html = self._generate_guidelines_html(khusus_guidelines, "Khusus")
                    wizard.performance_guidelines_khusus_html = khusus_html
                else:
                    wizard.performance_guidelines_khusus_html = False
                
                # Generate HTML for Kepemimpinan guidelines (only if has subordinates)
                if kepemimpinan_guidelines:
                    kepemimpinan_html = self._generate_guidelines_html(kepemimpinan_guidelines, "Kepemimpinan")
                    wizard.performance_guidelines_kepemimpinan_html = kepemimpinan_html
                else:
                    wizard.performance_guidelines_kepemimpinan_html = False
            else:
                wizard.performance_guidelines_umum_html = False
                wizard.performance_guidelines_khusus_html = False
                wizard.performance_guidelines_kepemimpinan_html = False
    
    def _generate_guidelines_html(self, guidelines, type_name):
        """Helper method to generate HTML for guidelines"""
        if not guidelines:
            return False
        
        # Determine the header based on type_name
        if type_name == "Umum":
            header_text = "Faktor Perilaku Kerja"
        elif type_name == "Khusus":
            header_text = "Hasil Kerja"
        else:  # Kepemimpinan
            header_text = "Faktor Perilaku Kerja"
            
        # Determine the display title based on type_name
        if type_name == "Umum":
            display_title = "Pedoman Penilaian Perilaku Kerja"
        elif type_name == "Khusus":
            display_title = "Pedoman Penilaian Hasil Kerja"
        else:  # Kepemimpinan
            display_title = "Pedoman Penilaian Kepemimpinan"
            
        html_content = f"""
        <style>
            .performance-guidelines-table-{type_name.lower()} {{
                width: 100%;
                border-collapse: collapse;
                border: 2px solid #444;
                font-size: 12px;
            }}
            .performance-guidelines-table-{type_name.lower()} th, 
            .performance-guidelines-table-{type_name.lower()} td {{
                border: 1px solid #444;
                padding: 6px;
                text-align: left;
                vertical-align: top;
            }}
            .performance-guidelines-table-{type_name.lower()} th {{
                background-color: #f2f2f2;
                font-weight: bold;
                font-size: 11px;
            }}
            .performance-guidelines-table-{type_name.lower()} tr:nth-child(even) {{
                background-color: #f9f9f9;
            }}
            .guidelines-header {{
                background-color: #e8f4f8;
                padding: 10px;
                margin-bottom: 15px;
                border-left: 4px solid #007bff;
            }}
        </style>
        <div class="guidelines-header">
            <h4>{display_title}</h4>
        </div>
        <table class="performance-guidelines-table-{type_name.lower()}">
            <thead>
                <tr>
                    <th>{header_text}</th>
                    <th>Definisi</th>
                    <th>NILAI 20%<br/>(Kurang Diterima)</th>
                    <th>NILAI 40%<br/>(Butuh Arahan)</th>
                    <th>NILAI 60%<br/>(Standart)</th>
                    <th>NILAI 80%<br/>(Performa Bagus)</th>
                    <th>NILAI 100%<br/>(Luar Biasa)</th>
                </tr>
            </thead>
            <tbody>
        """
        
        for guideline in guidelines:
            html_content += f"""
                <tr>
                    <td><strong>{guideline.factor or ''}</strong></td>
                    <td>{guideline.definition or ''}</td>
                    <td>{guideline.value_1 or ''}</td>
                    <td>{guideline.value_2 or ''}</td>
                    <td>{guideline.value_3 or ''}</td>
                    <td>{guideline.value_4 or ''}</td>
                    <td>{guideline.value_5 or ''}</td>
                </tr>
            """
        
        html_content += """
            </tbody>
        </table>
        """
        return html_content
    
    def action_close(self):
        """Close the wizard"""
        return {'type': 'ir.actions.act_window_close'}
