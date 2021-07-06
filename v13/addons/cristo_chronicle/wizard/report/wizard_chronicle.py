# -*- coding: utf-8 -*-
from odoo import api, fields, models, _
from odoo.tools import date_utils
from datetime import datetime
from odoo.addons.cristo.tools import cris_tools
from odoo.exceptions import UserError, ValidationError
from lxml import etree
import json

class WizardChronicle(models.TransientModel):
    _name = 'wizard.cristo.chronicle'
    _description = 'Cristo Chronicle'
    
    @api.model
    def default_get(self, fields):
        data = super(WizardChronicle, self).default_get(fields)
        if self.env.user.institute_id.id:
            data['institute_id'] = self.env.user.institute_id.id
        if self.env.user.rel_province_id.id:    
            data['rel_province_id'] = self.env.user.rel_province_id.id
        if self.env.user.community_id.id:
            data['community_ids'] = [(6,0,[self.env.user.community_id.id])]
        if self.env.user.institution_id.id:
            data['institution_ids'] = [(6,0,[self.env.user.institution_id.id])]
        return data
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(WizardChronicle, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        if self.user_has_groups('cristo.group_role_cristo_religious_province'):
            for node in doc.xpath("//field[@name='rel_province_id']"):
                modifiers = json.loads(node.get('modifiers'))
                modifiers['invisible'] = True
                node.set("modifiers", json.dumps(modifiers))
        if self.user_has_groups('cristo.group_role_cristo_religious_house'):
            for node in doc.xpath("//field[@name='rel_province_id']"):
                modifiers = json.loads(node.get('modifiers'))
                modifiers['invisible'] = True
                node.set("modifiers", json.dumps(modifiers))
            for node in doc.xpath("//group/group[2]/div[1]"):
                modifiers['invisible'] = True
                node.set("modifiers", json.dumps(modifiers))
            for node in doc.xpath("//group/group[2]/label[1]"):
                modifiers['invisible'] = True
                node.set("modifiers", json.dumps(modifiers))
        if self.user_has_groups('cristo.group_role_cristo_apostolic_institution'):
            for node in doc.xpath("//field[@name='rel_province_id']"):
                modifiers = json.loads(node.get('modifiers'))
                modifiers['invisible'] = True
                node.set("modifiers", json.dumps(modifiers))
            for node in doc.xpath("//group/group[2]/div[1]"):
                modifiers['invisible'] = True
                node.set("modifiers", json.dumps(modifiers))
            for node in doc.xpath("//group/group[2]/label[1]"):
                modifiers['invisible'] = True
                node.set("modifiers", json.dumps(modifiers))
            for node in doc.xpath("//group/group[2]/div[2]"):
                modifiers['invisible'] = True
                node.set("modifiers", json.dumps(modifiers))
            for node in doc.xpath("//group/group[2]/label[2]"):
                modifiers['invisible'] = True
                node.set("modifiers", json.dumps(modifiers))
#             for node in doc.xpath("//field[@name='community_ids']"):
#                 modifiers = json.loads(node.get('modifiers'))
#                 modifiers['invisible'] = True
#                 node.set("modifiers", json.dumps(modifiers))
#             for node in doc.xpath("//field[@name='institution_ids']"):
#                 modifiers = json.loads(node.get('modifiers'))
#                 modifiers['invisible'] = True
#                 node.set("modifiers", json.dumps(modifiers))
        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
    
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To", default=fields.Date.context_today)
    chronicle_type = fields.Selection([('summary','Report'),('album','Album')],string="Type", default="summary")
    institute_id = fields.Many2one('res.religious.institute', string="Congregation")
    rel_province_id = fields.Many2one('res.religious.province', string="Religious Province")
    community_ids = fields.Many2many('res.community', string="House/Community")
    institution_ids = fields.Many2many('res.institution', string="Institution")
    community_all = fields.Boolean(string="Community All", default=True)
    institution_all = fields.Boolean(string="Institution All", default=True)
    
    @api.constrains('date_from','date_to')
    def date_validation(self):
        if self.date_from and self.date_to:
            cris_tools.date_validation(self.date_from, self.date_to)
    
    @api.onchange('rel_province_id')
    def onchange_province(self):
        res = {}
        self.community_ids = False
        self.institution_ids = False
        res['domain'] = {'community_ids': [('rel_province_id', '=',self.rel_province_id.id)]}
        return res
    
    @api.onchange('community_all','community_ids','institution_all')
    def onchange_community(self):
        res = {}
        if self.community_all:
            self.community_ids = False
            res['domain'] = {'institution_ids': [('rel_province_id', '=',self.rel_province_id.id)]}
        else:
           res['domain'] = {'institution_ids': [('rel_province_id', '=',self.rel_province_id.id),('community_id', 'in',self.community_ids.ids)]}
        if self.institution_all:
            self.institution_ids = False
        if not self.community_ids:
            self.institution_ids = False
        return res
            
    def get_report_values(self):
        if self.community_all:
            chronicle_ids = self.env['cristo.chronicle'].search([('date','>=',self.date_from),('date','<=',self.date_to),('rel_province_id','=',self.rel_province_id.id)], order="date desc")
        elif not self.community_all:
            chronicle_ids = self.env['cristo.chronicle'].search([('date','>=',self.date_from),('date','<=',self.date_to),('rel_province_id','=',self.rel_province_id.id),('community_id','in',self.community_ids.ids)], order="date desc")
        elif self.institution_all:
            chronicle_ids = self.env['cristo.chronicle'].search([('date','>=',self.date_from),('date','<=',self.date_to),('rel_province_id','=',self.rel_province_id.id)], order="date desc")
        elif not self.institution_all:
            chronicle_ids = self.env['cristo.chronicle'].search([('date','>=',self.date_from),('date','<=',self.date_to),('rel_province_id','=',self.rel_province_id.id),('institution_id','in',self.institution_ids.ids)], order="date desc")
        
        if not chronicle_ids:
            raise ValidationError(_("No data found!."))
        elif self.chronicle_type == 'album' and not chronicle_ids.mapped('org_image_ids'):
            raise ValidationError(_("No data found!."))
        else:
            return chronicle_ids.ids
        
    def _build_contexts(self, data):
        result = {}
        result['date_from'] = 'date_from' in data['form'] and data['form']['date_from'] or ''
        result['date_to'] = 'date_to' in data['form'] and data['form']['date_to'] or ''
        result['chronicle_type'] = 'chronicle_type' in data['form'] and data['form']['chronicle_type'] or ''
        result['institute_id'] = 'institute_id' in data['form'] and data['form']['institute_id'] or ''
        result['rel_province_id'] = 'rel_province_id' in data['form'] and data['form']['rel_province_id'] or ''
        result['community_ids'] = 'community_ids' in data['form'] and data['form']['community_ids'] or ''
        result['institution_ids'] = 'institution_ids' in data['form'] and data['form']['institution_ids'] or ''
        result['community_all'] = 'community_all' in data['form'] and data['form']['community_all'] or ''
        result['institution_all'] = 'institution_all' in data['form'] and data['form']['institution_all'] or ''
        return result
    
    def print_pdf(self):
        self.ensure_one()
        values = self.get_report_values()
        data = {}
        data['values'] = values
        data['ids'] = self.env.context.get('active_ids', [])
        data['model'] = self.env.context.get('active_model', 'ir.ui.menu')
        data['form'] = self.read(['date_from','date_to','chronicle_type','institute_id','rel_province_id','community_ids','institution_ids','community_all','institution_all'])[0]
        self._build_contexts(data)
        return self.env.ref('cristo_chronicle.chronicle_report').report_action(self, data=data, config=False)
    
