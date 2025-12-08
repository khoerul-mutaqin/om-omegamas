from odoo import api, models


class HrLeave(models.Model):
    _inherit = "hr.leave"

    def action_approve(self, check_state=True):
        """
        Override approve behavior:
        - If employee has linked user and that user is portal, skip mail.activity actions
        - Otherwise fallback to normal behavior
        """
        for leave in self:
            employee = leave.employee_id
            user = employee.user_id
            if user and user.has_group("base.group_portal"):
                # Skip activity scheduling/feedback
                leave.write({"state": "validate"})
            else:
                # Default behavior (will trigger activities as usual)
                super().action_approve(check_state)
        return True
