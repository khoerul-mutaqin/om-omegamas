from odoo import models, fields, api

class AppraisalTemplate(models.Model):
    _name = 'appraisal.template'
    _description = 'Appraisal Template'

    name = fields.Char('Template Name', required=True)
    performance_guidelines_umum = fields.One2many(
        'performance.guidelines',
        'template_id_umum',
        string='Pedoman Penilaian Kerja Umum'
    )
    performance_guidelines_khusus = fields.One2many(
        'performance.guidelines',
        'template_id_khusus',
        string='Pedoman Penilaian Kerja Khusus'
    )
    performance_guidelines_kepemimpinan = fields.One2many(
        'performance.guidelines',
        'template_id_kepemimpinan',
        string='Pedoman Penilaian Kepemimpinan'
    )
    department_id = fields.Many2one(
        'hr.department', 
        string='Department'
    )
    atasan = fields.Boolean(
        string='Kepemimpinan',
        help='Check if this template is for managerial/leadership positions'
    )
    skill_types = fields.Many2many(
        'hr.skill.type',
        'appraisal_template_skill_type_rel',
        'template_id', 'skill_type_id',
        string='Skill Types'
    )
    skills = fields.Many2many(
        'hr.skill',
        'appraisal_template_skill_rel',
        'template_id', 'skill_id',
        string='Skills',
        domain="[('skill_type_id', 'in', skill_types)]"
    )
    skill_names = fields.Text(
        compute='_compute_skill_names',
        string='Skill Names',
        readonly=True
    )

    @api.depends('skills', 'skill_types')
    def _compute_skill_names(self):
        for record in self:
            if record.skills and record.skill_types:
                # Group skills by skill type
                skill_dict = {}
                for skill in record.skills:
                    skill_type_name = skill.skill_type_id.name or 'Uncategorized'
                    if skill_type_name not in skill_dict:
                        skill_dict[skill_type_name] = []
                    skill_dict[skill_type_name].append(skill.name)
                
                # Format the display
                lines = []
                for skill_type, skills in skill_dict.items():
                    lines.append(f"📋 {skill_type}:")
                    for skill in sorted(skills):
                        lines.append(f"   • {skill}")
                    lines.append("")  # Empty line between groups
                
                record.skill_names = '\n'.join(lines).strip()
            else:
                record.skill_names = ''
