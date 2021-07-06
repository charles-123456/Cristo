from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
from datetime import datetime

class ReportChronicle(models.AbstractModel):
    _name = 'report.cristo_chronicle.report_chronicle'
    _description = 'Cristo Chronicle'
    
    def get_dates(self, data):
        dt = []
        dates = self.env['cristo.chronicle'].search([('id','in',data['values'])],order='date asc')
        for date in dates:
            dt.append(date.date)
        return sorted(set(dt))
    
    def get_chronicle_ids(self, date):
        chronicle_ids = self.env['cristo.chronicle'].search([('date','=', date)])
        return chronicle_ids
        
    def _get_report_values(self, docids, data):
        self.model = self.env.context.get('active_model')
        return  {
            'doc_ids': self.ids,
            'doc_model': self.model,
                'data': data['form'],
                'docs': self.get_chronicle_ids,
            'get_dates': self.get_dates(data),
        }