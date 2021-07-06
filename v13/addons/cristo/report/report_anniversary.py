from odoo import models

class AnniversaryReport(models.AbstractModel):
    _name = "report.cristo.anniversary_report_template"
    _description = "Anniversary Report"
     
     
    def _get_report_values(self, docids, data=None):
        model = self.env.context.get('active_model')
        docs = self.env[model].browse(self.env.context.get('active_id'))
        return {
                'doc_ids': self.ids,
                'data' : data['form'],
                'doc_model': model,
                'docs': docs,
                'anniversary_list':data['anniversary_list'],
            }