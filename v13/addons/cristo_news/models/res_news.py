# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, _
from lxml import etree
import json

class ResNews(models.Model):
    _name = 'res.news'
    _description = "News"
    _order = 'create_date desc'

    name = fields.Char("Title", required=True)
    sequence = fields.Integer(string="Sequence")
    institute_id = fields.Many2one('res.religious.institute', string="Congregation")
    rel_province_id = fields.Many2one('res.religious.province', string="Religious Province")
    diocese_id = fields.Many2one('res.ecclesia.diocese', syring="Diocese")
    community_id = fields.Many2one('res.community', string="House/Community")
    state = fields.Selection([('publish','Publish'),('unpublished','Unpublished')],string="Status",default='publish')
    is_house = fields.Boolean(string="Show to my Houses")
    description = fields.Html(string="Description")
    parish_id = fields.Many2one('res.parish', string="Parish")

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ResNews, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                              submenu=submenu)
        doc = etree.XML(res['arch'])
        if view_type == 'search':
            for node in doc.xpath("//filter[@name='my_news']"):
                modifiers = []
                if self.user_has_groups('cristo.group_role_cristo_bsa_super_admin'):
                    modifiers = [(1, '=',1)]
                if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin'):
                    modifiers = [('institute_id', '=', self.env.user.institute_id.id)]
                if self.user_has_groups('cristo.group_role_cristo_religious_province'):
                    modifiers = [('rel_province_id', '=', self.env.user.rel_province_id.id)]
                if self.user_has_groups('cristo.group_role_cristo_religious_house') or self.user_has_groups('cristo.group_role_cristo_apostolic_institution')\
                        or self.user_has_groups('cristo.group_role_cristo_individual'):
                    modifiers = [('community_id', '=', self.env.user.community_id.id)]
                node.set("domain", json.dumps(modifiers))
        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res