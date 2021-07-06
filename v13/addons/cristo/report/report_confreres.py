from odoo import models, fields, api

class ReportStatisticsConfreres(models.AbstractModel):
    _name = 'report.cristo.statistics_confreres_report'
    _description = 'Statistics Confreres'
    
    def _get_report_values(self, docids, data):
        self.model = self.env.context.get('active_model')
        priest_ids = self.env['res.member'].search([('id','in',data['values'][0])], order= (data['values'][6]+' '+ data['form']['sort_rule']) if data['form']['sortby_id'] else '')
        community_ids = self.env['res.community'].search([('id', 'in', data['values'][7])])
        com = []
        for rec in community_ids:
            com.append(rec.name)
        communities = ', '.join(com)
        return  {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': priest_ids,
            'data': data['form'],
            'priests': data['values'][1],
            'deacons': data['values'][2],
            'brothers': data['values'][3],
            'lay_brothers': data['values'][4],
            'novices': data['values'][5],
            'community': communities,
        }