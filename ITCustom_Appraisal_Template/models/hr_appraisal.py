from odoo import models, fields, api, _
from odoo.exceptions import UserError
import logging

_logger = logging.getLogger(__name__)

class HrAppraisalSkill(models.Model):
    _inherit = 'hr.appraisal.skill'
    
    sequence = fields.Integer(string='Sequence', default=10)
    
    # Override field skill_level_id untuk membuat required=False
    skill_level_id = fields.Many2one(
        'hr.skill.level',
        compute='_compute_skill_level_id',
        domain="[('skill_type_id', '=', skill_type_id)]",
        store=True,
        readonly=False,
        required=False  # Ubah dari True menjadi False
    )
    
    bobot_penilaian = fields.Integer(
        string='Bobot Penilaian',
        related='skill_type_id.bobot_nilai',
        readonly=True,
        store=True,
        help='Bobot penilaian dalam persentase dari jenis skill ini'
    )
    
    bobot_penilaian_percentage = fields.Char(
        string='Bobot Penilaian Percentage',
        compute='_compute_bobot_penilaian_percentage',
        readonly=True,
        store=False,
        help='Bobot penilaian dengan tanda persen'
    )
    
    bobot_penilaian_points = fields.Integer(
        string='Bobot Penilaian Points',
        related='skill_type_id.bobot_nilai',
        readonly=True,
        store=True,
        help='Bobot penilaian dalam bentuk angka poin'
    )
    
    @api.depends('bobot_penilaian')
    def _compute_bobot_penilaian_percentage(self):
        for record in self:
            if record.bobot_penilaian:
                record.bobot_penilaian_percentage = f"{record.bobot_penilaian}%"
            else:
                record.bobot_penilaian_percentage = "0%"
    
    _order = "sequence, id"

    # Override compute method untuk handle optional skill_level_id
    @api.depends('skill_id')
    def _compute_skill_level_id(self):
        """Override compute method untuk handle optional skill_level_id"""
        for record in self:
            if not record.skill_id:
                record.skill_level_id = False
            else:
                skill_levels = record.skill_type_id.skill_level_ids
                record.skill_level_id = skill_levels.filtered('default_level') or skill_levels[0] if skill_levels else False

class HrAppraisal(models.Model):
    _inherit = 'hr.appraisal'

    memiliki_bawahan = fields.Boolean(string="Kepemimpinan")
    
    skill_type_averages = fields.Html(
        string="Skill Type Averages",
        compute="_compute_skill_type_averages",
        store=False,
    )
    
    performance_guidelines_umum_html = fields.Html(
        string="Performance Guidelines Umum",
        compute="_compute_performance_guidelines_html",
        store=False,
    )
    
    performance_guidelines_khusus_html = fields.Html(
        string="Performance Guidelines Khusus",
        compute="_compute_performance_guidelines_html",
        store=False,
    )
    
    @api.depends('department_id')
    def _compute_performance_guidelines_html(self):
        for appraisal in self:
            if appraisal.department_id:
                # Find appraisal templates that match the department_id
                matching_templates = self.env['appraisal.template'].search([
                    ('department_id', '=', appraisal.department_id.id)
                ])
                
                # Collect umum guidelines
                umum_guidelines = []
                for template in matching_templates:
                    umum_guidelines.extend(template.performance_guidelines_umum)
                
                # Collect khusus guidelines
                khusus_guidelines = []
                for template in matching_templates:
                    khusus_guidelines.extend(template.performance_guidelines_khusus)
                
                # Generate HTML for Umum guidelines
                if umum_guidelines:
                    umum_html = self._generate_guidelines_html(umum_guidelines, "Umum")
                    appraisal.performance_guidelines_umum_html = umum_html
                else:
                    appraisal.performance_guidelines_umum_html = False
                
                # Generate HTML for Khusus guidelines
                if khusus_guidelines:
                    khusus_html = self._generate_guidelines_html(khusus_guidelines, "Khusus")
                    appraisal.performance_guidelines_khusus_html = khusus_html
                else:
                    appraisal.performance_guidelines_khusus_html = False
            else:
                appraisal.performance_guidelines_umum_html = False
                appraisal.performance_guidelines_khusus_html = False
    
    def _generate_guidelines_html(self, guidelines, type_name):
        """Helper method to generate HTML for guidelines"""
        if not guidelines:
            return False
            
        html_content = f"""
        <style>
            .performance-guidelines-table-{type_name.lower()} {{
                width: 100%;
                border-collapse: collapse;
                border: 2px solid #444;
            }}
            .performance-guidelines-table-{type_name.lower()} th, 
            .performance-guidelines-table-{type_name.lower()} td {{
                border: 1px solid #444;
                padding: 8px;
                text-align: left;
            }}
            .performance-guidelines-table-{type_name.lower()} th {{
                background-color: #f2f2f2;
                font-weight: bold;
            }}
            .performance-guidelines-table-{type_name.lower()} tr:not(:last-child) td {{
                border-bottom: 1px solid #999;
            }}
        </style>
        <table class="performance-guidelines-table-{type_name.lower()}">
            <thead>
                <tr>
                    <th>Faktor Perilaku Kerja</th>
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
                    <td>{guideline.factor or ''}</td>
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
    
    def _convert_percentage_to_points(self, percentage, skill_type_id):
        """Convert percentage to point scale (0-N) based on skill type levels"""
        # Get all skill levels for this skill type, sorted by level_progress
        skill_levels = self.env['hr.skill.level'].search(
            [('skill_type_id', '=', skill_type_id)], 
            order='level_progress ASC'
        )
        
        if not skill_levels:
            return 0
            
        # Create mapping of level_progress to point values
        level_mapping = {}
        for i, level in enumerate(skill_levels):
            level_mapping[level.level_progress] = i
            
        # Get sorted level_progress values
        sorted_levels = sorted(level_mapping.keys())
        
        # Find the closest level
        for i in range(len(sorted_levels)):
            if percentage == sorted_levels[i]:
                return level_mapping[sorted_levels[i]]
            elif percentage < sorted_levels[i]:
                # If percentage is between two levels, round to the nearest one
                if i == 0:
                    return level_mapping[sorted_levels[0]]
                else:
                    prev_level_pct = sorted_levels[i-1]
                    curr_level_pct = sorted_levels[i]
                    # Calculate distances to both levels
                    dist_to_prev = percentage - prev_level_pct
                    dist_to_curr = curr_level_pct - percentage
                    # Return the closest level
                    if dist_to_prev <= dist_to_curr:
                        return level_mapping[prev_level_pct]
                    else:
                        return level_mapping[curr_level_pct]
        # If percentage is higher than the highest level, return the highest point value
        return level_mapping[sorted_levels[-1]] if sorted_levels else 0

    @api.depends('skill_ids', 'skill_ids.skill_type_id', 'skill_ids.level_progress')
    def _compute_skill_type_averages(self):
        for appraisal in self:
            if not appraisal.skill_ids:
                appraisal.skill_type_averages = ""
                continue
                
            # Group skills by skill type and their weight percentage (bobot_penilaian)
            skill_types_by_weight = {}
            skill_types_details = {}
            
            for skill in appraisal.skill_ids:
                if skill.skill_type_id:
                    weight = skill.bobot_penilaian or 0
                    skill_type_id = skill.skill_type_id.id
                    
                    # Store skill type details
                    if skill_type_id not in skill_types_details:
                        skill_types_details[skill_type_id] = {
                            'name': skill.skill_type_id.name,
                            'weight': weight
                        }
                    
                    # Group by weight
                    if weight not in skill_types_by_weight:
                        skill_types_by_weight[weight] = {}
                    
                    if skill_type_id not in skill_types_by_weight[weight]:
                        skill_types_by_weight[weight][skill_type_id] = []
                    
                    # Convert percentage to points and store
                    points = self._convert_percentage_to_points(skill.level_progress, skill.skill_type_id.id)
                    skill_types_by_weight[weight][skill_type_id].append(points)
            
            # Calculate averages for each weight group and final score
            averages_html = ""
            
            # Store group averages for final score calculation
            group_averages = []
            
            # Sort weights in descending order
            sorted_weights = sorted(skill_types_by_weight.keys(), reverse=True)
            
            for weight in sorted_weights:
                averages_html += f"<h4>Weight {weight}% Group:</h4>"
                
                # Calculate average for each skill type in this weight group
                group_total = 0
                group_count = 0
                
                for skill_type_id, points_values in skill_types_by_weight[weight].items():
                    if points_values:
                        skill_type_average = sum(points_values) / len(points_values)
                        skill_type_name = skill_types_details[skill_type_id]['name']
                        averages_html += f"<div style='margin-left: 20px;'><strong>{skill_type_name}:</strong> {skill_type_average:.2f} points</div>"
                        
                        # Add to group total for overall group average
                        group_total += skill_type_average
                        group_count += 1
                
                # Calculate overall group average
                if group_count > 0:
                    group_average = group_total / group_count
                    averages_html += f"<div style='margin-left: 20px; margin-top: 5px;'><strong>Group Average:</strong> {group_average:.2f} points</div>"
                    
                    # Store group average and weight for final score calculation
                    group_averages.append({
                        'average': group_average,
                        'weight': weight
                    })
                
                averages_html += "<br/>"
            
            # Calculate score
            score = 0
            calculation_details = []
            for group_data in group_averages:
                group_contribution = group_data['average'] * (group_data['weight'] / 100)
                score += group_contribution
                calculation_details.append(f"{group_data['average']:.2f} * {group_data['weight'] / 100:.2f}")
            
            # Calculate final score (Score * 20)
            final_score = score * 20
            
            # Add score and final score to the display
            calculation_string = " + ".join(calculation_details)
            averages_html += f"<div style='margin-top: 20px; padding-top: 10px; border-top: 1px solid #ccc;'><h4>Score Calculation:</h4>"
            averages_html += f"<div><strong>Formula:</strong> {calculation_string}</div>"
            averages_html += f"<div><strong>Score:</strong> {score:.2f} points</div>"
            averages_html += f"<div style='margin-top: 10px;'><h5><strong>Final Score: {final_score:.2f} points </strong><h5></div></div>"
            
            appraisal.skill_type_averages = averages_html

    def action_view_guidelines(self):
        """
        Action to open the performance guidelines wizard
        This method will be triggered by the 'Lihat Pedoman' button in the Skills tab
        """
        self.ensure_one()
        
        # Create wizard record
        wizard = self.env['performance.guidelines.wizard'].create({
            'appraisal_id': self.id,
        })
        
        return {
            'name': _('Pedoman Penilaian Kerja'),
            'type': 'ir.actions.act_window',
            'res_model': 'performance.guidelines.wizard',
            'view_mode': 'form',
            'res_id': wizard.id,
            'target': 'new',
            'view_id': self.env.ref('ITCustom_Appraisal_Template.view_performance_guidelines_wizard_form').id,
        }

    def action_get_skills_data(self):
        """
        Action to get skills data from appraisal templates based on department_id
        and atasan field, matching memiliki_bawahan status.
        This method will be triggered by the 'Get Data' button in the Skills tab
        """
        self.ensure_one()
        
        _logger.info("Starting action_get_skills_data for appraisal ID %s, department %s, memiliki_bawahan: %s",
                     self.id, self.department_id.name, self.memiliki_bawahan)
        
        # Initialize list for skills to add
        skills_to_add = []
        
        # Find appraisal templates that match both department_id and atasan field
        # Filter templates where atasan matches memiliki_bawahan
        matching_templates = self.env['appraisal.template'].search([
            ('department_id', '=', self.department_id.id),
            ('atasan', '=', self.memiliki_bawahan)
        ])
        _logger.info("Found %d matching templates for department %s with atasan=%s",
                     len(matching_templates), self.department_id.name, self.memiliki_bawahan)
        
        # Get skills from matching templates
        for template in matching_templates:
            skills_to_add.extend(template.skills.ids)
            _logger.info("Added %d skills from template %s (atasan=%s)", 
                         len(template.skills), template.name, template.atasan)
        
        # Remove duplicates
        skills_to_add = list(set(skills_to_add))
        _logger.info("Total unique skills to add: %d", len(skills_to_add))
        
        if not skills_to_add:
            raise UserError(_('No skills found in templates or leadership skills for department %s') % self.department_id.name)
        
        # DELETE ALL EXISTING SKILLS FIRST
        _logger.info("Deleting all existing skills for appraisal ID %s", self.id)
        if self.skill_ids:
            deleted_count = len(self.skill_ids)
            self.skill_ids.unlink()
            _logger.info("Deleted %d existing skills", deleted_count)
        
        # Sort skills by bobot_nilai (weight value) of their skill type
        # Group skills by bobot_nilai value
        skill_groups = {}
        for skill_id in skills_to_add:
            skill = self.env['hr.skill'].browse(skill_id)
            bobot_nilai = skill.skill_type_id.bobot_nilai or 0
            
            if bobot_nilai not in skill_groups:
                skill_groups[bobot_nilai] = []
            skill_groups[bobot_nilai].append(skill_id)
        
        # Sort the groups by bobot_nilai in descending order
        sorted_bobot_nilai = sorted(skill_groups.keys(), reverse=True)
        
        # Create appraisal skills, grouped by bobot_nilai
        created_skills = []
        for bobot_nilai in sorted_bobot_nilai:
            skill_ids = skill_groups[bobot_nilai]
            _logger.info("Processing %d skills with bobot_nilai %d%%", len(skill_ids), bobot_nilai)
            
            for skill_id in skill_ids:
                skill = self.env['hr.skill'].browse(skill_id)
                
                # Use skill's definisi as justification
                justification = skill.definisi or _('Tidak ada definisi untuk skill ini')
                
                # Create new appraisal skill dengan skill_level_id kosong (tidak diisi default)
                values = {
                    'appraisal_id': self.id,
                    'skill_type_id': skill.skill_type_id.id,
                    'skill_id': skill.id,
                    'skill_level_id': False,  # Kosongkan skill_level_id
                    'justification': justification,
                    'sequence': 100 - bobot_nilai,  # Lower sequence for higher bobot_nilai
                }
                
                new_skill = self.env['hr.appraisal.skill'].create(values)
                created_skills.append(new_skill)
                _logger.info("Created appraisal skill: %s (Type: %s, Skill Level: %s, Bobot Nilai: %d%%)",
                             skill.name, skill.skill_type_id.name, "Kosong", bobot_nilai)
        
        if created_skills:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Success'),
                    'message': _('%d skills have been loaded from appraisal templates and leadership skills for department %s, sorted by weight value') % (
                        len(created_skills), self.department_id.name),
                    'type': 'success',
                    'sticky': False,
                }
            }
        else:
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'title': _('Info'),
                    'message': _('All template and leadership skills are already present in this appraisal'),
                    'type': 'info',
                    'sticky': False,
                }
            }
