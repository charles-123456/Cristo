from odoo import models, fields, api

class ReportExpenditure(models.AbstractModel):
    _name = 'report.planner.expenditure_report'
    _description = 'Plan Expenditure'
    
    def _get_report_values(self, docids, data):
        self.model = self.env.context.get('active_model')
        docs = self.env[self.model].browse(self.env.context.get('active_ids'))
        if data['form']['all'] == True: 
            expenditure_ids = self.env['plan.expenditure'].search([])
        else:
            expenditure_ids = self.env['plan.expenditure'].search([('plan_id', 'in', data['form']['plan_ids'])])
            print(expenditure_ids)
        plan_ids = self.env['project.plan'].search([])
        return  {
            'doc_ids': self.ids,
            'doc_model': self.model,
            'docs': docs,
            'data': data['form'],
            'expenditure_ids': expenditure_ids,
            'plan_ids':plan_ids,
        }