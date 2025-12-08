# -*- coding: utf-8 -*-
from odoo import fields, models


class ProjectTask(models.Model):
    _inherit = 'project.task'

    # Override the user_ids field to allow portal users as assignees
    user_ids = fields.Many2many(
        'res.users',
        relation='project_task_user_rel',
        column1='task_id',
        column2='user_id',
        string='Assignees',
        context={'active_test': False},
        tracking=True,
        domain="[('active', '=', True)]"  # Allow both internal and portal users
    )
