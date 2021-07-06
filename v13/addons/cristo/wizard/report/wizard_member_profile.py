from odoo import models,fields,api


class MemberProfileReport(models.TransientModel):
    _name = "member.profile.report"
    
    ministry_type = fields.Selection([('minimum','Minimum'),('detailed','Detailed')], string="Member Ministry", default='minimum')

    def print_pdf(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['ministry_type'])[0]
        return self.env.ref('cristo.report_member_profile_base').report_action([], data=data)
     
