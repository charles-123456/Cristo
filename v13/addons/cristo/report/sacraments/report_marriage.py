from odoo import models, fields, api, _

class ReportMarriage(models.AbstractModel):
    _name = 'report.cristo.marriage_report_template'
    _description = 'Marriage'

    def _get_report_values(self, docids, data):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids'))
        marriage_ids = self.env['res.marriage'].search([('id','in',data['values'][0])])
        return  {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'data': data['form'],
            'marriage_ids': marriage_ids,
            'mrg_count': data['values'][1],
        }