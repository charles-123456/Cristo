from odoo import models, fields, api

class MemberProfileReport(models.TransientModel) :
    _name = "member.profile.report"

    type = fields.Selection([('minimum', 'Minimum'), ('detail','Detail')], string="Type")


    def print_pdf(self) :
        data = {}
        print('type',type)
        data['ids'] = self.env.context.get('active_ids', [])
        print('active_ids')
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['type'])[0]
        return self.env.ref('cristo.report_member_profile_base').report_action([], data=data)
