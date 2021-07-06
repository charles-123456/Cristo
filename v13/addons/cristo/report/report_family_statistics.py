from odoo import models, fields, api

class ReportStatisticsFamily(models.AbstractModel):
    _name = 'report.cristo.statistics_family_report'
    _description = 'Statistics Family'

    def _get_report_values(self, docids, data):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids'))
        return {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'data': data['form'],
            'family_list': data.get('family_list'),
        }