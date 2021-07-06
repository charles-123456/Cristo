from odoo import models, fields, api

class ReportActivity(models.AbstractModel):
    _name = 'report.planner.activity_report'
    _description = 'Plan Activity'

    # (Start_date >= FSD and strart_date <= FLD) or (end_date >= FSD and end_date <= FLD)

    def _get_report_values(self, docids, data):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids'))
        if data['form']['all'] == True: 
            activity_ids = self.env['plan.activity'].search(['|','&',('start_date','>=', data['form']['start_date']),('start_date','<=', data['form']['end_date']),'&',('end_date','>=', data['form']['start_date']),('end_date','<=', data['form']['end_date'])])
            plan_ids = self.env['project.plan'].search([])
        else:
            activity_ids = self.env['plan.activity'].search(['&','|','&',('start_date','>=', data['form']['start_date']),('start_date','<=', data['form']['end_date']),'&',('end_date','>=', data['form']['start_date']),('end_date','<=', data['form']['end_date']),('plan_id', 'in', data['form']['plan_ids'])])
            plan_ids = self.env['project.plan'].search([('id', 'in', data['form']['plan_ids'])])
        return  {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'data': data['form'],
            'activity_ids':activity_ids,
            'plan_ids':plan_ids,
        }