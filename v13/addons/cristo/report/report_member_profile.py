from odoo import models


class MemberProfileReport(models.AbstractModel):
    _name = "report.cristo.report_member_profile"
    _description = "Member Profile Report"
    
    
    def _get_report_values(self, docids, data):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids'))
        return {
                'doc_ids': self.ids,
                'doc_model': self.model,
                'data':data,
                'docs': docs,
            }