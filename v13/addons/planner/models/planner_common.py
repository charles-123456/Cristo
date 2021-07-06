# -*- coding: utf-8 -*-
from odoo import models, fields, api, _

class CommonPlanSection(models.AbstractModel):
    _name = "common.plan.section"
    _description = 'Common Plan Section'
    
    @api.model
    def default_get(self, fields):
        data = super(CommonPlanSection, self).default_get(fields)
        if self._context.get('default_plan_id'):
            data['plan_id'] = self._context.get('default_plan_id')
        return data
    
    plan_id = fields.Many2one('project.plan', string="Project Plan", ondelete='cascade')
    plan_sec1 = fields.Boolean(compute='_compute_plan_sections')
    plan_sec2 = fields.Boolean(compute='_compute_plan_sections')
    plan_sec3 = fields.Boolean(compute='_compute_plan_sections')
    plan_sec4 = fields.Boolean(compute='_compute_plan_sections')

    @api.depends('plan_id')
    def _compute_plan_sections(self):
        self.plan_sec1 = self.plan_sec2 = self.plan_sec3 = self.plan_sec4 = False
        for rec in self:
            if rec.plan_id:
                rec.plan_sec1 = True if rec.plan_id.section1 == 'yes' else False
                rec.plan_sec2 = True if rec.plan_id.section2 == 'yes' else False
                rec.plan_sec3 = True if rec.plan_id.section3 == 'yes' else False
                rec.plan_sec4 = True if rec.plan_id.section4 == 'yes' else False
                