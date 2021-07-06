# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from datetime import datetime, date
from odoo.addons.cristo.tools import cris_tools
from odoo.exceptions import UserError, ValidationError

class Marriage(models.TransientModel):
    _name = 'wizard.marriage'
    _description = 'Marriage Report Wizard'
    
    @api.constrains('start_date','end_date')
    def date_validation(self):
        if self.start_date and self.end_date:
            cris_tools.date_validation(self.start_date, self.end_date)
    
    parish_id = fields.Many2one('res.parish', string='Parish')
    start_date = fields.Date(string="Date From")
    end_date = fields.Date(string="Date To") 
    mrg_date_range = fields.Selection([('this_year', 'This Year-To Date'), ('last_year', 'Last Year'), ('custom', 'Custom')], 
                                  string="Date of Marriage", default="this_year")
    
    
    @api.onchange('mrg_date_range')
    def onchange_marriage_date_range(self):
        if self.mrg_date_range == 'this_year':
            year = '%s-01-01' % date.today().year
            self.start_date = datetime.strptime(year, '%Y-%m-%d')
            self.end_date = datetime.today().strftime('%Y-%m-%d')
        elif self.mrg_date_range == 'last_year':
            y = int(date.today().year)-1
            year1 = '%s-01-01' % y
            year2 = '%s-12-31' % y
            self.start_date = datetime.strptime(year1, '%Y-%m-%d')
            self.end_date = datetime.strptime(year2, '%Y-%m-%d') 
        elif self.mrg_date_range == 'custom':
            self.start_date = datetime.today().strftime('%Y-%m-%d') 
            self.end_date = datetime.today().strftime('%Y-%m-%d')
            
    def _build_contexts(self, data):
        result = {}
        result['parish_id'] = 'parish_id' in data['form'] and data['form']['parish_id'] or ''
        result['start_date'] = 'start_date' in data['form'] and data['form']['start_date'] or ''
        result['end_date'] = 'end_date' in data['form'] and data['form']['end_date'] or ''
        result['mrg_date_range'] = 'mrg_date_range' in data['form'] and data['form']['mrg_date_range'] or ''
        return result
    
    def get_parish_marriage_data(self):
        marriage_ids = self.env['res.marriage'].search([('parish_id','=', self.parish_id.id),('mrg_date','>=', self.start_date),('mrg_date','<=', self.end_date)])
        if not marriage_ids:
            raise UserError(_('No Data Found'))
        marriage_count = len(marriage_ids)
        return [marriage_ids.ids,marriage_count]
        
    def print_pdf(self):
        self.ensure_one()
        data = {}
        data['values'] = self.get_parish_marriage_data()
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('parish_id', 'ir.ui.menu')
        data['form'] = self.read(['parish_id','start_date','end_date','mrg_date_range'])[0]
        self._build_contexts(data)
        return self.env.ref('cristo.sacrament_marriage_report').report_action(self, data=data, config=False)