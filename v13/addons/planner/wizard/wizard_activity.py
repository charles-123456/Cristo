# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
from datetime import datetime, timedelta, date
from dateutil.relativedelta import relativedelta
from odoo.exceptions import UserError
import calendar
from odoo.addons.planner.tools import planner_tools

class Activity(models.TransientModel):
    _name = 'wizard.activity'
    _description = 'Activities'

    plan_ids = fields.Many2many('project.plan', string="Plan")
    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    all = fields.Boolean(string="All")
    duration = fields.Selection([('this week','This Week'),('last week','Last Week'),('this month','This Month'),('last month','Last Month'),('custom','custom')], string="Duration")
    
    @api.onchange('start_date','end_date')
    def onchange_date(self):
        if self.start_date and self.end_date:
            if self.start_date > self.end_date:
                self.start_date = False
                return {'warning': {
                        'title': _('Date Validation'),
                        'message': _('Start date is greater than end date')}
                    }

    @api.onchange('duration')
    def _onchange_duration(self):
        if self.duration == 'this week':
            self.start_date, self.end_date = planner_tools.get_current_week_date()
        if self.duration == 'last week':
            self.start_date, self.end_date = planner_tools.get_last_week_date()
        if self.duration == 'this month':
            self.start_date, self.end_date = planner_tools.get_current_month_date()
        if self.duration == 'last month':
            self.start_date, self.end_date = planner_tools.get_last_month_date()
        if self.duration == 'custom':
            self.start_date, self.end_date = '', ''

    @api.onchange('all')
    def onchange_all(self):
        if self.all:
            self.plan_ids = self.env['project.plan'].search([])
        else:
            self.plan_ids = False
        
    def _build_contexts(self, data):
        result = {}
        result['plan_ids'] = 'plan_ids' in data['form'] and data['form']['plan_ids'] or ''
        result['start_date'] = 'start_date' in data['form'] and data['form']['start_date'] or ''
        result['end_date'] = 'end_date' in data['form'] and data['form']['end_date'] or ''
        result['all'] = 'all' in data['form'] and data['form']['all'] or ''
        result['duration'] = 'duration' in data['form'] and data['form']['duration'] or ''
        return result
    
    def print_activity(self):
        self.ensure_one()
        data = {}
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['plan_ids','start_date','end_date','all','duration'])[0]
        self._build_contexts(data)
        return self.env.ref('planner.plan_activity').report_action(self, data = data, config=False)