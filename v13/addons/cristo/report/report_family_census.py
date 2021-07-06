from odoo import models, fields, api

class ReportFamilyCensus(models.AbstractModel):
    _name = 'report.cristo.family_census_report'
    _description = 'Family Census'

    def get_family_list(self, data):
        family_ids = self.env['res.family'].search([('parish_bcc_id','in',data['form']['bcc_ids'])])
        return family_ids
    
        
    
    def _get_report_values(self, docids, data):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids'))
        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'data': data['form'],
            'get_family_list': self.get_family_list(data),
        }