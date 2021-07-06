# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from lxml import etree
import json
from odoo.exceptions import UserError

Mail_Excluded_Fields = ['message_bounce','message_channel_ids','message_partner_ids','message_main_attachment_id','message_ids','message_follower_ids',
                        'message_needaction','message_is_follower','message_has_error']
Partner_Excluded_Fields = ['activity_ids','activity_exception_decoration','additional_info','channel_ids','company_id','company_name',
                         'commercial_company_name','commercial_partner_id','partner_gid','credit_limit','display_name',
                         'partner_latitude','partner_longitude','image_256','image_512','image_1024','image_1920','image_128',
                         'function','known_as','lang','calendar_last_notif_ack','activity_date_deadline',
                         'activity_summary','email_normalized','occupation_id','parent_name','team_id','user_id','partner_id','activity_user_id','partner_share',
                         'signup_token','signup_expiration','signup_type','vat','user_ids','tz','bank_ids','employee','is_company',
                         'parent_id','activity_type_id','ref','is_blacklisted','type','color','category_id','child_ids','industry_id','association_id']


class CommonReligiousFields(models.AbstractModel):
    _name = "common.rel.fields"
    _description = "Common Religious Fields"
    
    @api.model
    def default_get(self, fields):
        data = super(CommonReligiousFields, self).default_get(fields)
        data['institute_id'] = self.env.user.institute_id.id
        data['rel_province_id'] = self.env.user.rel_province_id.id
        data['community_id'] = self.env.user.community_id.id
        data['institution_id'] = self.env.user.institution_id.id
        return data
    
    def view_for_admin(self):
        if self.user_has_groups('base.group_erp_manager') or self.user_has_groups('cristo.group_role_cristo_bsa_super_admin'):
            return True
        else:
            return False
    
    @api.depends('rel_province_id')
    def get_province_value(self):
        if self.rel_province_id :
            self.check_province = True
        else:
            self.check_province = self.view_for_admin()
        
    @api.depends('community_id')
    def get_community_value(self):
        if self.community_id :
            self.check_community = True
        else:
            self.check_community = self.view_for_admin()
            
    @api.depends('institute_id')
    def get_congregation_value(self):
        if self.institute_id :
            self.check_congregation = True
        else:
            self.check_congregation = self.view_for_admin()
            
    @api.depends('institution_id')
    def get_institution_value(self):
        if self.institution_id :
            self.check_institution = True
        else:
            self.check_institution = self.view_for_admin()
                    
    
    institute_id = fields.Many2one('res.religious.institute', string="Congregation", ondelete="restrict")
    rel_province_id = fields.Many2one('res.religious.province', string="Religious Province", ondelete="restrict")   
    community_id = fields.Many2one('res.community', string="House/Community", ondelete="restrict",copy=False)
    institution_id = fields.Many2one('res.institution', string="Institution", ondelete="restrict")
    check_community = fields.Boolean(compute='get_community_value')
    check_province = fields.Boolean(compute='get_province_value')
    check_congregation = fields.Boolean(compute='get_congregation_value')
    check_institution = fields.Boolean(compute='get_institution_value')


    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(CommonReligiousFields, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin,cristo.group_role_cristo_religious_province,cristo.group_role_cristo_religious_house,cristo.group_role_cristo_apostolic_institution,cristo.group_role_cristo_individual'):
            for node in doc.xpath("//field[@name='institute_id']"):
                modifiers = json.loads(node.get('modifiers'))
                modifiers['invisible'] = True
                node.set("modifiers", json.dumps(modifiers))
        if self.user_has_groups('cristo.group_role_cristo_religious_province,cristo.group_role_cristo_religious_house,cristo.group_role_cristo_apostolic_institution,cristo.group_role_cristo_individual'):
#             for node in doc.xpath("//field[@name='institute_id']"):
#                 modifiers = json.loads(node.get('modifiers'))
#                 modifiers['invisible'] = True
#                 node.set("modifiers", json.dumps(modifiers))
            for node in doc.xpath("//field[@name='rel_province_id']"):
                modifiers = json.loads(node.get('modifiers'))
                modifiers['invisible'] = True
                node.set("modifiers", json.dumps(modifiers))
        if self.user_has_groups('cristo.group_role_cristo_religious_house,cristo.group_role_cristo_apostolic_institution,cristo.group_role_cristo_individual'):
#             for node in doc.xpath("//field[@name='institute_id']"):
#                 modifiers = json.loads(node.get('modifiers'))
#                 modifiers['invisible'] = True
#                 node.set("modifiers", json.dumps(modifiers))
#             for node in doc.xpath("//field[@name='rel_province_id']"):
#                 modifiers = json.loads(node.get('modifiers'))
#                 modifiers['invisible'] = True
#                 node.set("modifiers", json.dumps(modifiers))
            for node in doc.xpath("//field[@name='community_id']"):
                modifiers = json.loads(node.get('modifiers'))
                modifiers['invisible'] = True
                node.set("modifiers", json.dumps(modifiers))
        if self.user_has_groups('cristo.group_role_cristo_apostolic_institution,cristo.group_role_cristo_individual'):
#             for node in doc.xpath("//field[@name='institute_id']"):
#                 modifiers = json.loads(node.get('modifiers'))
#                 modifiers['invisible'] = True
#                 node.set("modifiers", json.dumps(modifiers))
#             for node in doc.xpath("//field[@name='rel_province_id']"):
#                 modifiers = json.loads(node.get('modifiers'))
#                 modifiers['invisible'] = True
#                 node.set("modifiers", json.dumps(modifiers))
#             for node in doc.xpath("//field[@name='community_id']"):
#                 modifiers = json.loads(node.get('modifiers'))
#                 modifiers['invisible'] = True
#                 node.set("modifiers", json.dumps(modifiers))
            for node in doc.xpath("//field[@name='institution_id']"):
                modifiers = json.loads(node.get('modifiers'))
                modifiers['invisible'] = True
                node.set("modifiers", json.dumps(modifiers))
        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res


class CommonEcclesiaFields(models.AbstractModel):
    _name = "common.ecc.fields"
    _description = "Common Eccleasia Fields"

    @api.model
    def default_get(self, fields):
        data = super(CommonEcclesiaFields, self).default_get(fields)
        data['diocese_id'] = self.env.user.diocese_id.id
        data['vicariate_id'] = self.env.user.vicariate_id.id
        data['parish_id'] = self.env.user.parish_id.id
        return data

    def view_for_admin(self):
        if self.user_has_groups('base.group_erp_manager') or self.user_has_groups('cristo.group_role_cristo_bsa_super_admin'):
            return True
        else:
            return False

    @api.depends('diocese_id')
    def check_diocese_value(self):
        if self.diocese_id:
            self.check_diocese = True
        else:
            self.check_diocese = self.view_for_admin()

    @api.depends('vicariate_id')
    def check_vicariate_value(self):
        if self.vicariate_id:
            self.check_vicariate = True
        else:
            self.check_vicariate = self.view_for_admin()

    @api.depends('parish_id')
    def check_parish_value(self):
        if self.parish_id:
            self.check_parish = True
        else:
            self.check_parish = self.view_for_admin()

    diocese_id = fields.Many2one('res.ecclesia.diocese', string="Diocese", ondelete="restrict")
    vicariate_id = fields.Many2one('res.vicariate', string="Vicariate", ondelete="restrict")
    parish_id = fields.Many2one('res.parish', string="Parish", ondelete="restrict")
    check_diocese = fields.Boolean(compute='check_diocese_value')
    check_vicariate = fields.Boolean(compute='check_vicariate_value')
    check_parish = fields.Boolean(compute='check_parish_value')

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(CommonEcclesiaFields, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar,
                                                                 submenu=submenu)
        doc = etree.XML(res['arch'])
        if self.user_has_groups('cristo.group_role_cristo_diocese'):
            for node in doc.xpath("//field[@name='diocese_id']"):
                modifiers = json.loads(node.get('modifiers'))
                modifiers['invisible'] = True
                node.set("modifiers", json.dumps(modifiers))
        if self.user_has_groups('cristo.group_role_cristo_vicarate'):
            for node in doc.xpath("//field[@name='diocese_id']"):
                modifiers = json.loads(node.get('modifiers'))
                modifiers['invisible'] = True
                node.set("modifiers", json.dumps(modifiers))
            for node in doc.xpath("//field[@name='vicariate_id']"):
                modifiers = json.loads(node.get('modifiers'))
                modifiers['invisible'] = True
                node.set("modifiers", json.dumps(modifiers))
        if self.user_has_groups('cristo.group_role_cristo_parish_ms') or self.user_has_groups('cristo.group_role_cristo_bcc') or self.user_has_groups('cristo.group_role_cristo_family') or self.user_has_groups('cristo.group_role_cristo_individual'):
            for node in doc.xpath("//field[@name='diocese_id']"):
                modifiers = json.loads(node.get('modifiers'))
                modifiers['invisible'] = True
                node.set("modifiers", json.dumps(modifiers))
            for node in doc.xpath("//field[@name='vicariate_id']"):
                modifiers = json.loads(node.get('modifiers'))
                modifiers['invisible'] = True
                node.set("modifiers", json.dumps(modifiers))
            for node in doc.xpath("//field[@name='parish_id']"):
                modifiers = json.loads(node.get('modifiers'))
                modifiers['invisible'] = True
                node.set("modifiers", json.dumps(modifiers))
        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
    
class ResPartner(models.Model):
    _name = 'res.partner'
    _inherit = ['res.partner','common.rel.fields','common.ecc.fields']
    
    association_id = fields.Many2one('res.association', ondelete="restrict", string="Association")
    occupation_id = fields.Many2one('res.occupation',string="Occupation")

class RecordArchiveAccess(models.AbstractModel):
    _name = "record.archive.access"
    _description = "Record Archive Access"

    def action_archive(self):
        for rec in self:
            try:
                rec.check_access_rights('write')
                rec.check_access_rule('write')
            except:
                raise UserError(_("Sorry! you are not allowed to archive the selected record(s)"))
        return self.filtered(lambda record: record.active).toggle_active()

    def action_unarchive(self):
        for rec in self:
            try:
                rec.check_access_rights('write')
                rec.check_access_rule('write')
            except:
                raise UserError(_("Sorry! you are not allowed to unarchive the selected record(s)"))
        return self.filtered(lambda record: not record.active).toggle_active()