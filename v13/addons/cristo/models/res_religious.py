# -*- coding: utf-8 -*-
from odoo import fields, api, models, _
from datetime import datetime,date,timedelta
from lxml import etree
import json
from odoo.osv import expression
from odoo.exceptions import UserError, ValidationError
from odoo.addons.cristo.tools import cris_tools
from odoo.addons.base.models.ir_mail_server import MailDeliveryException
from odoo.tools import format_datetime
import base64
from odoo.addons.cristo.models.res_common import Partner_Excluded_Fields, Mail_Excluded_Fields


GENERATE_YEAR = []
cur_year = datetime.now().year
while(cur_year >= 1800):
    GENERATE_YEAR.append((str(cur_year), str(cur_year)))
    cur_year -= 1

DAYS = []
for d in range(1, 32):
    DAYS.append((str(d),str(d)))
    
MONTHS = [
        ('1', 'January'),
        ('2', 'February'),
        ('3', 'March'),
        ('4', 'April'),
        ('5', 'May'),
        ('6', 'June'),
        ('7', 'July'),
        ('8', 'August'),
        ('9', 'September'),
        ('10', 'October'),
        ('11', 'November'),
        ('12', 'December'),
    ]

Common_Excluded_Fields = Partner_Excluded_Fields + Mail_Excluded_Fields
Institute_Excluded_Fields = ['cri_code','ecclesiastical_statistics_ids','education_statistics_ids','formation_statistics_ids','healthcare_statistics_ids',
                             'media_statistics_ids','member_statistics_ids','pastoral_statistics_ids','retreat_animation_statistics_ids','welfare_statistics_ids',
                             'institution_count','members_count','community_count','province_count','region_count','zone_community_count','vicariate_id','parish_id','diocese_id',
                             'house_ids','member_ids','institution_ids','news_ids','rel_province_ids','rel_region_ids','rel_zone_ids','institute_id','rel_province_id','community_id','institution_id'] + Common_Excluded_Fields
Province_Excluded_Fields = ['cri_code','ecclesiastical_statistics_ids','education_statistics_ids','formation_statistics_ids','healthcare_statistics_ids',
                            'media_statistics_ids','member_statistics_ids','pastoral_statistics_ids','retreat_animation_statistics_ids','welfare_statistics_ids',
                            'institution_count','members_count','community_count','zone_community_count','vicariate_id','parish_id','diocese_id','file_ids',
                            'house_ids','member_ids','institution_ids','news_ids','rel_zone_ids','rel_province_id','community_id','institution_id','cir_header_img','outside_country_members'] + Common_Excluded_Fields
Community_Excluded_Fields = ['institution_count','members_count','vicariate_id','parish_id','diocese_id','house_member_ids','institution_ids','member_ids',
                             'community_id','institution_id',] + Common_Excluded_Fields
Institution_Excluded_Fields = ['members_count','vicariate_id','parish_id','diocese_id','member_ids','institution_id',] + Common_Excluded_Fields
Region_Excluded_Fields = ['province_count','vicariate_id','parish_id','diocese_id','rel_province_id','community_id','institution_id'] + Common_Excluded_Fields

class ReligiousInstitute(models.Model):
    _name = 'res.religious.institute'
    _description = 'Religious Institute'
    _inherits = {'res.partner':'partner_id'}
    _inherit = ['mail.thread','partner.clear.cache','record.archive.access']
    _custom_filter_exclude_fields = Institute_Excluded_Fields
    
    @api.model
    def default_get(self, fields):
        data = super(ReligiousInstitute, self).default_get(fields)
        main_category = self.env['res.main.category'].search([('code', '=', 'RC')], limit=1)
        data['main_category_id'] = main_category.id or []
        data['company_type'] = 'company'
        return data
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            domain = ['|', ('name', operator, name), ('code', operator, name)]
        rec = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(rec).with_user(name_get_uid))
    
    def open_regions(self):
        action = self.env.ref('cristo.action_religious_region').read()[0]
        action.update({
            'domain': [('institute_id','=',self.id)],
            'context': "{'default_institute_id':%d}" % (self.id),
        })
        return action
    
    def open_zone_communities(self):
        action = self.env.ref('cristo.action_religious_zone').read()[0]
        action.update({
            'domain': [('institute_id','=',self.id)],
            'context': "{'default_institute_id':%d}" % (self.id),
        })
        return action
    
    def open_communities(self):
        action = self.env.ref('cristo.action_religious_community').read()[0]
        action.update({
            'domain': [('institute_id','=',self.id)],
            'context': "{'default_institute_id':%d}" % (self.id),
        })
        return action
    
    def open_institutions(self):
        action = self.env.ref('cristo.action_institution').read()[0]
        action.update({
            'domain': [('institute_id','=',self.id)],
            'context': "{'default_institute_id':%d}" % (self.id),
        })
        return action
    
    def open_religious_province(self):
        action = self.env.ref('cristo.action_religious_province').read()[0]
        action.update({
            'domain': [('institute_id','=',self.id)],
            'context': "{'default_institute_id':%d}" % (self.id),
           })
        return action
    
    def open_members(self):
        action = self.env.ref('cristo.action_all_member').read()[0]
        action.update({
            'domain': [('institute_id','=',self.id)],
            'context': "{'default_institute_id':%d}" % (self.id),
        })
        return action
    
    def _compute_region_count(self):
        self.region_count = len(self.rel_region_ids)
        
    def _compute_province_count(self):
        self.province_count = len(self.rel_province_ids)
             
    def _compute_zone_community_count(self):
        self.zone_community_count = len(self.rel_zone_ids)
    
    def _compute_community_count(self):
        self.community_count = len(self.house_ids)
    
    def _compute_institution_count(self):
        self.institution_count = len(self.institution_ids)
        
    def _compute_members_count(self):
        self.members_count = len(self.member_ids)
        
    partner_id = fields.Many2one('res.partner', string="Contact", ondelete="cascade", required=True)
    sup_called_id = fields.Many2one('res.member.role', string="Institute Superior Called as")
    superior_id = fields.Many2one('res.member', string="Superior Name", compute='_compute_superior_name')
    founder = fields.Char(string="Founder")
    patron_id = fields.Many2one('res.patron', string="Patron")
    institute_type = fields.Selection([('priest','Priests'),('lay_brother','Lay Brothers'),('brother','Brothers'),('sister_apostolic','Sisters (Apostolic)'),('sister_contemplative','Sisters (Contemplative)'),('secular_institute','Secular Institute')], string="Type of Institute")
    institute_category_ids = fields.Many2many('res.institution.category', string="Main forms of Ministry")
    motto = fields.Char(string="Motto")
    mission = fields.Char(string="Mission")
    origin_country_id = fields.Many2one('res.country', string="Origin Country", ondelete="restrict")
    establishment_year = fields.Selection(GENERATE_YEAR, string="Year of Establishment")
    arrival_year = fields.Selection(GENERATE_YEAR, string="Year of Arrival")
    history = fields.Html(string="History")
    charism = fields.Char(string="Charism")
    registered_name = fields.Char(string="Registered Name")
    rel_province_id = fields.Many2one('res.religious.province', string="Province", ondelete="restrict")
    feast_day = fields.Selection(DAYS,string="Feast Day")
    feast_month = fields.Selection(MONTHS,string="Feast Month")
    community_id = fields.Many2one('res.community', string="House/Community Address", tracking=True)
    rel_region_ids = fields.One2many('res.religious.region','institute_id',string="Region(s)")
    rel_province_ids = fields.One2many('res.religious.province','institute_id',string="Province(s)")
    rel_zone_ids = fields.One2many('res.religious.zone','institute_id',string="Area")
    house_ids = fields.One2many('res.community','institute_id',string="House(s)")
    institution_ids = fields.One2many('res.institution','institute_id',string="Institution(s)")
    member_ids = fields.One2many('res.member','institute_id',string="Member(s)")
    region_count = fields.Integer(compute="_compute_region_count", string="Regions")
    province_count = fields.Integer(compute='_compute_province_count', string="Province Count")
    community_count = fields.Integer(compute="_compute_community_count", string="House")
    institution_count = fields.Integer(compute="_compute_institution_count", string="Institutions")
    zone_community_count = fields.Integer(compute="_compute_zone_community_count", string="Area")
    members_count = fields.Integer(compute="_compute_members_count", string="Member")
    street = fields.Char(string="street", related="community_id.street", store=True)
    street2 = fields.Char(string="street2", related="community_id.street2", store=True)
    place = fields.Char(string="Place", related="community_id.place", store=True)
    city = fields.Char(string="City", related="community_id.city", store=True)
    district_id = fields.Many2one("res.state.district", string="District", related="community_id.district_id", store=True)
    state_id = fields.Many2one("res.country.state", string="State", related="community_id.state_id", store=True)
    country_id = fields.Many2one("res.country", string="Country", related="community_id.country_id", store=True)
    zip = fields.Char(string="Zip", related="community_id.zip", store=True)
    is_authorize = fields.Boolean(compute="_compute_check_authorize")
    important_date_ids = fields.One2many('res.important.date','institute_id', string="Important Dates", domain=[('type','=','important_date')])
    feast_date_ids = fields.One2many('res.important.date', 'institute_id', string="Feast Dates", domain=[('type','=','feast_date')])

    def _compute_check_authorize(self):
        for rec in self:
            rec.is_authorize = False
            if self.user_has_groups('cristo.group_role_cristo_bsa_super_admin'):
                rec.is_authorize = True
            elif self.user_has_groups('cristo.group_role_cristo_religious_institute_admin') and self.env.user.institute_id.id == rec.id:
                rec.is_authorize = True
    
    def _compute_superior_name(self):
        self.superior_id = False
        if self.community_id:
            hm_ids = self.community_id.house_member_ids.ids
            if self.ri_sup_called_id:
                house_mem_ids = self.env['house.member'].search([('status','=','active'),('id','in',hm_ids)])
                role_id = house_mem_ids.mapped('member_role_ids').filtered(lambda hmr:self.ri_sup_called_id.id in hmr.role_ids.ids)
                if role_id:
                    self.superior_id = role_id.house_member_id.member_id.id if role_id == 1 else role_id.house_member_id.member_id[0].id  
    
    def open_religious_province(self):
        action = self.env.ref('cristo.action_religious_province').read()[0]
        action.update({
            'domain': [('institute_id','=',self.id)],
            'context': {'default_institute_id':self.id}
           })
        return action
    
    def unlink(self):
        contacts = self.mapped('partner_id')
        super(ReligiousInstitute, self).unlink()
        return contacts.unlink()
    
class ReligiousRegion(models.Model):
    _name = 'res.religious.region'
    _description = 'Religious Region'
    _inherits = {'res.partner':'partner_id'}
    _inherit = ['address.loading','mail.thread','partner.clear.cache','record.archive.access']
    _custom_filter_exclude_fields = Region_Excluded_Fields

    @api.model
    def default_get(self, fields):
        data = super(ReligiousRegion, self).default_get(fields)
        main_category = self.env['res.main.category'].search([('code', '=', 'RR')], limit=1)
        data['main_category_id'] = main_category.id or []
        data['company_type'] = 'company'
        data['institute_id'] = self.env.user.institute_id.id
        return data
    
    def open_provinces(self):
        action = self.env.ref('cristo.action_religious_province').read()[0]
        action.update({
            'domain': [('institute_id','=',self.institute_id.id)],
            'context': {'default_rel_region_id':self.id,'default_institute_id':self.institute_id.id }
        })
        return action
    
    @api.depends('institute_id')
    def _compute_province_count(self):
        self.province_count = self.env['res.religious.province'].sudo().search_count([('institute_id','=',self.institute_id.id)])
    
    partner_id = fields.Many2one('res.partner', string="Contact", ondelete="cascade", required=True)
    institute_id = fields.Many2one('res.religious.institute', string="Congregation", ondelete='restrict', tracking=True)
    house_id = fields.Many2one('res.community', string="House/Community Address", ondelete="restrict", tracking=True)
    sup_called_id = fields.Many2one('res.member.role', string="Region Superior Called as")
    superior_id = fields.Many2one('res.member', string="Superior Name", compute='_compute_superior_name')
    province_count = fields.Integer(compute="_compute_province_count", string="Provinces")
    street = fields.Char(string="street", related="house_id.street", store=True)
    street2 = fields.Char(string="street2", related="house_id.street2", store=True)
    place = fields.Char(string="Place", related="house_id.place", store=True)
    city = fields.Char(string="City", related="house_id.city", store=True)
    district_id = fields.Many2one("res.state.district", string="District", related="house_id.district_id", store=True)
    state_id = fields.Many2one("res.country.state", string="State", related="house_id.state_id", store=True)
    country_id = fields.Many2one("res.country", string="Country", related="house_id.country_id", store=True)
    zip = fields.Char(string="Zip", related="house_id.zip", store=True)
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ReligiousRegion, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin') or self.user_has_groups('cristo.group_role_cristo_religious_province') or self.user_has_groups('cristo.group_role_cristo_religious_house') or self.user_has_groups('cristo.group_role_cristo_apostolic_institution'):
            for node in doc.xpath("//field[@name='institute_id']"):
                modifiers = json.loads(node.get('modifiers'))
                modifiers['invisible'] = True
                node.set("modifiers", json.dumps(modifiers))
        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
    
    def _compute_superior_name(self):
        self.superior_id = False
        if self.house_id:
            hm_ids = self.house_id.house_member_ids.ids
            if self.sup_called_id:
                house_mem_ids = self.env['house.member'].search([('status','=','active'),('id','in',hm_ids)])
                role_id = house_mem_ids.mapped('member_role_ids').filtered(lambda hmr:self.sup_called_id.id in hmr.role_ids.ids)
                if role_id:
                    self.superior_id = role_id.house_member_id.member_id.id if role_id == 1 else role_id.house_member_id.member_id[0].id  
    
    def unlink(self):
        contacts = self.mapped('partner_id')
        super(ReligiousRegion, self).unlink()
        return contacts.unlink()
    
class ReligiousProvince(models.Model):
    _name = 'res.religious.province'
    _description = 'Religious Province'
    _inherits = {'res.partner':'partner_id'}
    _inherit = ['address.loading', 'mail.thread','partner.clear.cache','record.archive.access']
    _custom_filter_exclude_fields = Province_Excluded_Fields

    @api.model
    def default_get(self, fields):
        data = super(ReligiousProvince, self).default_get(fields)
        main_category = self.env['res.main.category'].search([('code', '=', 'RP')], limit=1)
        data['main_category_id'] = main_category.id or []
        data['company_type'] = 'company'
        data['institute_id'] = self.env.user.institute_id.id
        return data
    
    @api.model
    def _name_search(self, name, args=None, operator='ilike', limit=100, name_get_uid=None):
        args = args or []
        if operator == 'ilike' and not (name or '').strip():
            domain = []
        else:
            domain = ['|', ('name', operator, name), ('code', operator, name)]
        rec = self._search(expression.AND([domain, args]), limit=limit, access_rights_uid=name_get_uid)
        return models.lazy_name_get(self.browse(rec).with_user(name_get_uid))
    
    def name_get(self):
        result = []
        for record in self:
            if record.code:
                result.append((record.id, "%s" % (record.name) +  " (%s)" % (record.code)))
            elif record.institute_id.code:
                result.append((record.id, "%s" % (record.name) +  " (%s)" % (record.institute_id.code)))
            else:
                result.append((record.id,record.name))
        return result
    
    def open_zone_communities(self):
        action = self.env.ref('cristo.action_religious_zone').read()[0]
        action.update({
            'domain': [('rel_province_id','=',self.id)],
            'context': "{'default_rel_province_id': %d, 'default_institute_id':%d}" % (self.id,self.institute_id.id),
        })
        return action
    
    def open_communities(self):
        action = self.env.ref('cristo.action_religious_community').read()[0]
        action.update({
            'domain': [('rel_province_id','=',self.id)],
            'context': "{'default_rel_province_id':%d,'default_institute_id':%d}" % (self.id,self.institute_id.id),
        })
        return action
    
    def open_institutions(self):
        action = self.env.ref('cristo.action_institution').read()[0]
        action.update({
            'domain': [('rel_province_id','=',self.id)],
            'context': "{'default_rel_province_id':%d,'default_institute_id':%d}" % (self.id,self.institute_id.id),
        })
        return action
    
    def open_members(self):
        action = self.env.ref('cristo.action_all_member').read()[0]
        action.update({
            'domain': [('rel_province_id','=',self.id)],
            'context': "{'default_rel_province_id':%d,'default_institute_id':%d}" % (self.id,self.institute_id.id),
        })
        return action

    def open_diocese(self):
        if self.diocese_ids:
            action = self.env.ref('cristo.action_ecclesia_diocese').read()[0]
            action.update({
                'domain': [('id','in',self.diocese_ids.ids)],
            })
            return action
        else:
            raise UserError(_("The diocese covered field seems to be empty. Kindly fill it."))
    
    def _compute_zone_community_count(self):
        self.zone_community_count = len(self.rel_zone_ids)
    
    def _compute_community_count(self):
        self.community_count = len(self.house_ids)
    
    def _compute_institute_count(self):
        self.institution_count = len(self.institution_ids)
        
    def _compute_members_count(self):
        self.members_count = len(self.member_ids)
        
    def _compute_diocese_count(self):
        self.diocese_count = len(self.diocese_ids)
        
    partner_id = fields.Many2one('res.partner', string="Contact", ondelete="cascade", required=True)
    establishment_year = fields.Selection(GENERATE_YEAR, string="Year of Establishment")
    sup_called_id = fields.Many2one('res.member.role', string="Province Superior Called as")
    superior_id = fields.Many2one('res.member', string="Superior Name", compute='_compute_superior_name')
    rel_region_id = fields.Many2one('res.religious.region', string="Region", ondelete="restrict", tracking=True)
    history = fields.Html(string="History")
    institute_id = fields.Many2one('res.religious.institute', string='Congregation',ondelete='restrict', tracking=True)
    house_id = fields.Many2one('res.community', string="House/Community Address", ondelete="restrict" , tracking=True)
    diocese_ids = fields.Many2many('res.ecclesia.diocese',string="Diocese Covered")
    community_count = fields.Integer(compute="_compute_community_count", string="Communities")
    institution_count = fields.Integer(compute="_compute_institute_count", string="Institutions")
    zone_community_count = fields.Integer(compute="_compute_zone_community_count", string="Area")
    members_count = fields.Integer(compute="_compute_members_count", string="Member")
    rel_zone_ids = fields.One2many('res.religious.zone','rel_province_id',string="Zone(s)")
    house_ids = fields.One2many('res.community','rel_province_id',string="House(s)")
    institution_ids = fields.One2many('res.institution','rel_province_id',string="Institution(s)")
    member_ids = fields.One2many('res.member','rel_province_id',string="Member(s)")
    street = fields.Char(string="street", related="house_id.street", store=True)
    street2 = fields.Char(string="street2", related="house_id.street2", store=True)
    place = fields.Char(string="Place", related="house_id.place", store=True)
    city = fields.Char(string="City", related="house_id.city", store=True)
    district_id = fields.Many2one("res.state.district",string="District", related="house_id.district_id", store=True)
    state_id = fields.Many2one("res.country.state", string="State", related="house_id.state_id", store=True)
    country_id = fields.Many2one("res.country", string="Country", related="house_id.country_id", store=True)
    zip = fields.Char(string="Zip", related="house_id.zip", store=True)
    head_role_ids = fields.Many2many('res.member.role', string="Main Head Roles")
    important_date_ids = fields.One2many('res.important.date', 'rel_province_id', string="Important Dates",
                                         domain=[('type','=','important_date')])
    feast_date_ids = fields.One2many('res.important.date', 'rel_province_id', string="Feast Dates",
                                     domain=[('type','=','feast_date')])
    institute_type = fields.Selection([('priest','Priests'),('lay_brother','Lay Brothers'),('brother','Brothers'),('sister_apostolic','Sisters (Apostolic)'),('sister_contemplative','Sisters (Contemplative)'),('secular_institute','Secular Institute')], string="Type of Institute")
    org_renewals_ids = fields.One2many('res.renewals', 'rel_province_id', string="Province Renewals")
    is_authorize = fields.Boolean(compute="_compute_check_authorize")
    custom_area_label = fields.Char(string="Custom Area Label")
    
#   These fields are used to capture the additional basic details for every province
    data_source = fields.Selection([('static','Static'),('extract','Extract')], string="Data Source", default='static')
    high_lev_province_ids = fields.One2many('higher.level.rel_province.people', 'rel_province_id', string="Higher Level Province People")
    no_of_member_ids = fields.One2many('rel.province.statistics', 'rel_province_id', string="Number of Members")
    no_of_institution_ids = fields.One2many('rel.province.statistics', 'rel_pro_institution_id', string="Number of Institutions")
    pro_diff_state_ids = fields.Many2many('res.country.state', string="Province in Different States")
    no_of_communities = fields.Integer(string="No of Communities")
    apostolate = fields.Text(string="Apostolate")
    other_centers = fields.Text(string="Other Centers")
    formation_house = fields.Text(string="Formation House")
    common_house = fields.Text(string="Members Common House", help="Members working in common house")
    vision = fields.Char(string="Vision")
    mission = fields.Char(string="Mission")
    outside_country_members = fields.Integer(string="Outside Country Members ", help="Number of Members working outside the country.")
    diocese_count = fields.Integer(compute="_compute_diocese_count", string="Diocese")

   
    def _compute_check_authorize(self):
        for rec in self:
            rec.is_authorize = False
            if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin,cristo.group_role_cristo_bsa_super_admin'):
                rec.is_authorize = True
            elif self.user_has_groups('cristo.group_role_cristo_religious_province') and self.env.user.rel_province_id.id == rec.id:
                rec.is_authorize = True
    
    def _compute_superior_name(self):
        for rec in self:
            rec.superior_id = False
            if rec.sup_called_id:
                role_id = rec.member_ids.filtered(lambda mem: rec.sup_called_id.id in mem.role_ids.ids)
                if role_id:
                    rec.superior_id = role_id[0].id

    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ReligiousProvince, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin') or self.user_has_groups('cristo.group_role_cristo_religious_province') or self.user_has_groups('cristo.group_role_cristo_religious_house') or self.user_has_groups('cristo.group_role_cristo_apostolic_institution'):
            if view_type == 'form':
                for node in doc.xpath("//field[@name='institute_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
        if self.user_has_groups('cristo.group_role_cristo_religious_province'):
            if view_type == 'tree':
                for node in doc.xpath("/tree"):
                    node.set("decoration-success", "id == %d" % (self.env.user.rel_province_id.id))
        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res

    def province_renewals(self):
        action = self.env.ref('cristo.action_org_renewals').read()[0]
        action.update({
            'domain': [('rel_province_id', '=', self.id),('community_id','=',False)],
            'context': {'default_rel_province_id':self.id},
            'target': 'current',
        })
        return action

    def unlink(self):
        contacts = self.mapped('partner_id')
        super(ReligiousProvince, self).unlink()
        return contacts.unlink()       
                      
class ReligiousZone(models.Model):
    _name = 'res.religious.zone'
    _description = 'Religious Zone'
    _inherits = {'res.partner':'partner_id'}
    _inherit = ['address.loading','mail.thread','partner.clear.cache','record.archive.access']
    _custom_filter_exclude_fields = Common_Excluded_Fields

    @api.model
    def default_get(self, fields):
        data = super(ReligiousZone, self).default_get(fields)
        main_category = self.env['res.main.category'].search([('code', '=', 'RZ')], limit=1)
        data['main_category_id'] = main_category.id or []
        data['company_type'] = 'company'
        data['institute_id'] = self.env.user.institute_id.id
        data['rel_province_id'] = self.env.user.rel_province_id.id or self._context.get('default_rel_province_id')
        return data
    
    def open_communities(self):
        action = self.env.ref('cristo.action_religious_community').read()[0]
        action.update({
            'domain': [('rel_zone_id','=',self.id)],
            'context': "{'default_rel_zone_id':%d,'default_rel_province_id':%d ,'default_institute_id':%d}" % (self.id,self.rel_province_id.id,self.institute_id.id),
        })
        return action
    
    def open_institutions(self):
        action = self.env.ref('cristo.action_institution').read()[0]
        action.update({
            'domain': [('rel_zone_id','=',self.id)],
            'context': "{'default_rel_zone_id':%d,'default_rel_province_id':%d ,'default_institute_id':%d}" % (self.id,self.rel_province_id.id,self.institute_id.id),
        })
        return action
    
    def _compute_community_count(self):
        self.community_count = len(self.house_ids)
    
    def _compute_institute_count(self):
        self.institution_count = len(self.institution_ids)
    
    partner_id = fields.Many2one('res.partner', string="Contact", ondelete="cascade", required=True)
    institute_id = fields.Many2one('res.religious.institute', string='Congregation',ondelete='restrict', tracking=True)
    rel_province_id = fields.Many2one('res.religious.province', string="Province", ondelete="restrict", tracking=True)
    institute_id = fields.Many2one('res.religious.institute', string='Congregation',ondelete='restrict')
    rel_province_id = fields.Many2one('res.religious.province', string="Province", ondelete="restrict")
    areas_covered = fields.Text(string="Areas Covered")
    community_count = fields.Integer(compute="_compute_community_count", string="House")
    institution_count = fields.Integer(compute="_compute_institute_count", string="Institutions")
    house_ids = fields.One2many('res.community','rel_zone_id',string="House(s)")
    institution_ids = fields.One2many('res.institution','rel_zone_id',string="Institution(s)")
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ReligiousZone, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin') or self.user_has_groups('cristo.group_role_cristo_religious_province') or self.user_has_groups('cristo.group_role_cristo_religious_house') or self.user_has_groups('cristo.group_role_cristo_apostolic_institution'):
            for node in doc.xpath("//field[@name='institute_id']"):
                modifiers = json.loads(node.get('modifiers'))
                modifiers['invisible'] = True
                node.set("modifiers", json.dumps(modifiers))
        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res
    
    def unlink(self):
        contacts = self.mapped('partner_id')
        super(ReligiousZone, self).unlink()
        return contacts.unlink()
    
class ReligiousCommunity(models.Model):
    _name = 'res.community'
    _description = 'Religious House/Community'
    _inherits = {'res.partner':'partner_id'}
    _inherit = ['address.loading','mail.thread','partner.clear.cache','record.archive.access']
    _custom_filter_exclude_fields = Community_Excluded_Fields
    _order = 'name'

    @api.model
    def default_get(self, fields):
        data = super(ReligiousCommunity, self).default_get(fields)
        main_category = self.env['res.main.category'].search([('code', '=', 'HC')], limit=1)
        data['main_category_id'] = main_category.id or []
        data['company_type'] = 'company'
        data['institute_id'] = self.env.user.institute_id.id
        data['rel_province_id'] = self.env.user.rel_province_id.id or self._context.get('default_rel_province_id')
        return data
    
    def name_get(self):
        result = []
        for record in self:
            if record.district_id:
                result.append((record.id, "{} ({})".format(record.name, record.district_id.name)))
            elif record.city:
                result.append((record.id, "{} ({})".format(record.name, record.city)))
            else:
                result.append((record.id,record.name))
        return result
    
    def open_institutions(self):
        action = self.env.ref('cristo.action_institution').read()[0]
        action.update({
            'domain': [('community_id','=',self.id)],
            'context': "{'default_community_id': %d,'default_institute_id':%d,'default_rel_province_id':%d,'default_rel_zone_id':%d}" % (self.id,self.institute_id.id,self.rel_province_id.id,self.rel_zone_id.id)
        })
        return action
    
    def open_members(self):
        action = self.env.ref('cristo.action_all_member').read()[0]
        action.update({
            'domain': [('community_id','=',self.id)],
            'context': "{'default_community_id': %d,'default_institute_id':%d,'default_rel_province_id':%d,'default_rel_zone_id':%d}" % (self.id,self.institute_id.id,self.rel_province_id.id,self.rel_zone_id.id)
        })
        return action
    
    def open_ecclesia_members(self):
        action = self.env.ref('cristo.action_all_member').read()[0]
        action.update({
            'domain': [('ecc_community_id','=',self.id),('membership_type','=','SE')],
            'context': "{'default_ecc_community_id': %d,'default_membership_type': '%s'}" % (self.id, 'SE')
        })
        return action
    
    def open_member_history(self):
        action = self.env.ref('cristo.action_house_members').read()[0]
        action.update({
            'domain':[('house_id', '=', self.id)]
        })
        return action
    
    def _compute_institution_count(self):
        self.institution_count = len(self.institution_ids)
    
    def _compute_members_count(self):
        self.members_count = len(self.member_ids)
        
    def _compute_ecc_members_count(self):
        self.ecc_members_count = self.env['res.member'].search_count([('ecc_community_id','=',self.id),('membership_type','=','SE')]) 
    
    partner_id = fields.Many2one('res.partner', string="Contact", ondelete="cascade", required=True)    
    institute_id = fields.Many2one('res.religious.institute', string="Congregation", ondelete="restrict", tracking=True) 
    rel_province_id = fields.Many2one('res.religious.province', string="Province", ondelete="restrict", tracking=True) 
    rel_zone_id = fields.Many2one('res.religious.zone', string="Area", ondelete="restrict", tracking=True)
    patron_id = fields.Many2one('res.patron', string="Patron", ondelete="restrict")
    establishment_year = fields.Selection(GENERATE_YEAR, string="Year of Establishment")
    canonical_year = fields.Selection(GENERATE_YEAR, string="Year of Canonical Erection")
    enable_zone = fields.Boolean(string="Enable Zone")
    diocese_id = fields.Many2one('res.ecclesia.diocese', string="Diocese", ondelete="restrict")
    parish_id = fields.Many2one('res.parish', ondelete="restrict", string="Parish", tracking=True)
    house_member_ids = fields.One2many('house.member', 'house_id', string="House Member", domain=[('status', '=', 'active')])
    institution_count = fields.Integer(compute="_compute_institution_count", string="Institutions")
    members_count = fields.Integer(compute="_compute_members_count", string="Member")
    sup_called_id = fields.Many2one('res.member.role', string="Community Superior Called as")
    superior_id = fields.Many2one('res.member', string="Superior Name", compute='_compute_superior_name')
    position_ids = fields.Many2many('res.member.role',string="Position",compute='_compute_superior_name')
    institution_ids = fields.One2many('res.institution','community_id', string="Institution(s)")
    member_ids = fields.One2many('res.member','community_id',string="Member(s)")
    history = fields.Html(string="History")
    benefactors = fields.Text(string="Benefactors")
    founder = fields.Char(string="Founder")
    owned_by = fields.Selection([('religious','Religious'),('diocese','Diocese')],string="Owned By")
    is_authorize = fields.Boolean(compute="_compute_check_authorize")
    org_renewals_ids = fields.One2many('res.renewals', 'community_id', string="Province Renewals")
    ministry_ids = fields.Many2many('res.institution.category', string="Ministry")
    important_date_ids = fields.One2many('res.important.date', 'community_id', string="Important Dates",
                                         domain=[('type','=','important_date')])
    feast_date_ids = fields.One2many('res.important.date', 'community_id', string="Feast Dates",
                                     domain=[('type','=','feast_date')])
    ecc_members_count = fields.Integer(compute="_compute_ecc_members_count", string="Member(s)")
    
    def _compute_check_authorize(self):
        for rec in self:
            rec.is_authorize = False
            if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin,cristo.group_role_cristo_bsa_super_admin,base.group_erp_manager'):
                rec.is_authorize = True
            elif self.user_has_groups('cristo.group_role_cristo_religious_house') and self.env.user.community_id.id == rec.id:
                rec.is_authorize = True
            elif self.user_has_groups('cristo.group_role_cristo_religious_province') and self.env.user.rel_province_id.id == rec.rel_province_id.id:
                rec.is_authorize = True
            
            
    def _compute_superior_name(self):
        for rec in self:
            rec.superior_id = False
            rec.position_ids = False
            if rec.house_member_ids:
                if rec.sup_called_id:
#                 house_mem_ids = self.env['house.member'].search([('date_to','=',False),('id','in',self.house_member_ids)])
                    role_id = rec.house_member_ids.mapped('member_role_ids').filtered(lambda hmr:rec.sup_called_id.id in hmr.role_ids.ids)
                    if role_id:
                        rec.superior_id = role_id.house_member_id.member_id.id if role_id == 1 else role_id.house_member_id.member_id[0].id
                        rec.position_ids = role_id.house_member_id.role_ids
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(ReligiousCommunity, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        if view_type == 'form':
            if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin'):
                for node in doc.xpath("//field[@name='institute_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
            if self.user_has_groups('cristo.group_role_cristo_religious_province'):            
                for node in doc.xpath("//field[@name='institute_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
                for node in doc.xpath("//field[@name='rel_province_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
            if self.user_has_groups('cristo.group_role_cristo_religious_house'):            
                for node in doc.xpath("//field[@name='institute_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
                for node in doc.xpath("//field[@name='rel_province_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
            if self.user_has_groups('cristo.group_role_cristo_apostolic_institution'):            
                for node in doc.xpath("//field[@name='institute_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
                for node in doc.xpath("//field[@name='rel_province_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
        if view_type == "search":
            if self.user_has_groups('cristo.group_role_cristo_religious_province'):
                for node in doc.xpath("//filter[@name='my_houses']"):
                    modifiers = [('rel_province_id', '=', self.env.user.rel_province_id.id)]
                    node.set("domain", json.dumps(modifiers))
        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res

    def house_renewals(self):
        action = self.env.ref('cristo.action_org_renewals').read()[0]
        action.update({
            'domain': [('community_id', '=', self.id),('institution_id','=',False)],
            'context': {'default_community_id': self.id},
            'target': 'current',
        })
        return action
    
    @api.model
    def create(self, vals):
        res = super(ReligiousCommunity, self).create(vals)
        if self.user_has_groups('cristo.group_role_cristo_religious_province'):
            if res.rel_province_id != self.env.user.rel_province_id:
                raise UserError(_("Sorry! You cannot create other province House/Community."))
        return res
    
    def write(self, vals):
        province_id = vals.get('rel_province_id', False) or self.rel_province_id.id
        if self.user_has_groups('cristo.group_role_cristo_religious_province'):
            if province_id != self.env.user.rel_province_id.id:
                raise UserError(_("Sorry! You cannot create other province House/Community."))
        return super(ReligiousCommunity, self).write(vals)
        
    def unlink(self):
        contacts = self.mapped('partner_id')
        super(ReligiousCommunity, self).unlink()
        return contacts.unlink()
    
    # This is For REST API 
    def api_get_community_position(self,values):
        role_result = []
        role_ids = self.env['res.member.role'].browse(values)
        for role in role_ids:
            roles = {}
            roles['role_id'] = role.id
            roles['role_name'] = role.name
            role_result.append(roles)
        return role_result
    
    # This is For REST API 
    def api_get_ministry(self,values):
        ministry_result = []
        ministry_ids = self.env['res.institution.category'].browse(values)
        for ministry in ministry_ids:
            ministrys = {}
            ministrys['ministry_id'] = ministry.id
            ministrys['ministry_name'] = ministry.name
            ministry_result.append(ministrys)
        return ministry_result
    
class Institution(models.Model):
    _name = 'res.institution'
    _description = 'Institution'
    _inherits = {'res.partner':'partner_id'}
    _inherit = ['address.loading', 'mail.thread','partner.clear.cache','record.archive.access']
    _custom_filter_exclude_fields = Institution_Excluded_Fields

    @api.model
    def default_get(self, fields):
        data = super(Institution, self).default_get(fields)
        main_category = self.env['res.main.category'].search([('code', '=', 'RI')], limit=1)
        data['main_category_id'] = main_category.id or []
        data['company_type'] = 'company'
        data['community_id'] = self.env.user.community_id.id or self._context.get('default_community_id')
        data['institute_id'] = self.env.user.institute_id.id
        data['rel_province_id'] = self.env.user.rel_province_id.id or self._context.get('default_rel_province_id')
        return data
    
    def name_get(self):
        result = []
        for record in self:
            if record.community_id:
                result.append((record.id, "{} ({})".format(record.name, record.community_id.name)))
            else:
                result.append((record.id,record.name))
        return result
    
    def open_members(self):
        action = self.env.ref('cristo.action_all_member').read()[0]
        action.update({
            'domain': [('id','=',self.member_ids.mapped('member_id.id'))],
            'context': "{'default_community_id': %d,'default_institute_id':%d,'default_rel_province_id':%d}" % (self.community_id.id,self.institute_id.id,self.rel_province_id.id)
        })
        return action
    
    def open_ecclesia_members(self):
        action = self.env.ref('cristo.action_all_member').read()[0]
        action.update({
            'domain': [('ecc_community_id','=',self.id),('membership_type','=','SE')],
            'context': "{'default_ecc_community_id': %d,'default_membership_type': '%s'}" % (self.community_id.id, 'SE')
        })
        return action
    
    def open_house_member_role_history(self):
        action = self.env.ref('cristo.action_house_member_role').read()[0]
        action.update({
            'domain':[('institution_id', '=', self.id)]
        })
        return action
    
    def _compute_members_count(self):
        self.members_count = self.env['res.member'].search_count([('id','=',self.member_ids.mapped('member_id.id'))])
    
    def _compute_ecc_members_count(self):
        self.ecc_members_count = self.env['res.member'].search_count([('ecc_community_id','=',self.id),('membership_type','=','SE')])
    
    partner_id = fields.Many2one('res.partner', string="Contact", ondelete="cascade", required=True)
    diocese_id = fields.Many2one('res.ecclesia.diocese', string="Diocese", ondelete="restrict")
    parish_id = fields.Many2one('res.parish', string="Parish", ondelete="restrict", tracking=True)
    institute_id = fields.Many2one('res.religious.institute', string="Congregation", ondelete="restrict", tracking=True)
    community_id = fields.Many2one('res.community', string="House/Community", ondelete="restrict", tracking=True)
    establishment_date = fields.Date(string="Establishment Date")
    institution_category_id = fields.Many2one('res.institution.category', string="Ministry", ondelete="restrict")
    ministry_category_id = fields.Many2one('res.institution.category', string="Category", ondelete="restrict", tracking=True)
    category_type_id = fields.Many2one('res.institution.category', string="Type", ondelete="restrict")    
    rel_province_id = fields.Many2one('res.religious.province', string="Province", ondelete="restrict", tracking=True)
    rel_zone_id = fields.Many2one('res.religious.zone', string="Area", ondelete="restrict", tracking=True)
    superior_name = fields.Char(string="Institution Head", tracking=True)
    use_community_address = fields.Boolean(string="House/Community Address")
    member_ids = fields.One2many('house.member.role', 'institution_id', string="Member Role", domain=[('status', '=', 'active')])
    members_count = fields.Integer(compute="_compute_members_count", string="Member")
    history = fields.Html(string="History")
    org_renewals_ids = fields.One2many('res.renewals', 'institution_id', string="Province Renewals")
    is_authorize = fields.Boolean(compute="_compute_check_authorize")
    ministry_ids = fields.Many2many('res.institution.category', string="All Ministry")
    important_date_ids = fields.One2many('res.important.date','institution_id', string="Important Dates")
    medium = fields.Many2one('res.languages', string="Medium")
    board = fields.Many2one('institution.board', string="Board")
    is_school = fields.Boolean(string="School",compute="_compute_is_school", readonly=False)
    ecc_members_count = fields.Integer(compute="_compute_ecc_members_count", string="Member(s)")
    
    @api.depends('ministry_ids','ministry_category_id')
    def _compute_is_school(self):
        for rec in self:
            rec.is_school = False
            if rec.ministry_ids:
                val_ids = self.env['res.institution.category'].search(['|','|',('name','ilike','school'),('name','ilike','secondary'),('name','ilike','Higher Education'), ('id', 'in', rec.ministry_ids.ids)])
                if val_ids:
                    rec.is_school = True
            if rec.ministry_category_id and rec.ministry_category_id.parent_id.name == 'Education':
                    rec.is_school = True
            
    def _compute_check_authorize(self):
         for rec in self:
            rec.is_authorize = False
            if self.user_has_groups('cristo.group_role_cristo_religious_house,cristo.group_role_cristo_religious_province,cristo.group_role_cristo_religious_institute_admin,cristo.group_role_cristo_bsa_super_admin'):
                rec.is_authorize = True
            elif self.user_has_groups('cristo.group_role_cristo_apostolic_institution') and self.env.user.institution_id.id == rec.id:
                rec.is_authorize = True
    
    @api.constrains('mobile', 'country_id')
    def _check_mobile(self):
        if self.country_id.code == 'IN':
            if self.mobile:
                cris_tools.mobile_validation(self.mobile)    
    
    @api.onchange('use_community_address')
    def onchange_use_community_address(self):
        if self.community_id and self.use_community_address:
            self.street = self.community_id.street
            self.street2 = self.community_id.street2
            self.place = self.community_id.place
            self.city = self.community_id.city
            self.district_id = self.community_id.district_id
            self.state_id = self.community_id.state_id
            self.zip = self.community_id.zip
            self.country_id = self.community_id.country_id
        else:
            self.street = self.street2 = self.place = self.city = self.district_id = self.state_id = self.zip = self.country_id = False
    
    @api.model
    def fields_view_get(self, view_id=None, view_type='form', toolbar=False, submenu=False):
        res = super(Institution, self).fields_view_get(view_id=view_id, view_type=view_type, toolbar=toolbar, submenu=submenu)
        doc = etree.XML(res['arch'])
        if view_type == 'form':
            if self.user_has_groups('cristo.group_role_cristo_religious_institute_admin'):
                for node in doc.xpath("//field[@name='institute_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
            if self.user_has_groups('cristo.group_role_cristo_religious_province'):            
                for node in doc.xpath("//field[@name='institute_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
                for node in doc.xpath("//field[@name='rel_province_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
            if self.user_has_groups('cristo.group_role_cristo_religious_house'):            
                for node in doc.xpath("//field[@name='institute_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
                for node in doc.xpath("//field[@name='rel_province_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
                for node in doc.xpath("//field[@name='community_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
            if self.user_has_groups('cristo.group_role_cristo_apostolic_institution'):            
                for node in doc.xpath("//field[@name='institute_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
                for node in doc.xpath("//field[@name='rel_province_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
                for node in doc.xpath("//field[@name='community_id']"):
                    modifiers = json.loads(node.get('modifiers'))
                    modifiers['invisible'] = True
                    node.set("modifiers", json.dumps(modifiers))
            
#                 for node in doc.xpath("//field[@name='rel_province_id']"):
#                     modifiers = json.loads(node.get('modifiers'))
#                     modifiers['invisible'] = True
#                     node.set("modifiers", json.dumps(modifiers))
        if view_type == "search":
            if self.user_has_groups('cristo.group_role_cristo_religious_province'):
                for node in doc.xpath("//filter[@name='my_institutions']"):
                    modifiers = [('rel_province_id', '=', self.env.user.rel_province_id.id)]
                    node.set("domain", json.dumps(modifiers))
        res['arch'] = etree.tostring(doc, encoding='unicode')
        return res

    def institution_renewals(self):
        action = self.env.ref('cristo.action_org_renewals').read()[0]
        action.update({
            'domain': [('institution_id', '=', self.id)],
            'context': {'default_institution_id':self.id},
            'target': 'current',
        })
        return action

    @api.model
    def create(self, vals):
        res = super(Institution, self).create(vals)
        if self.user_has_groups('cristo.group_role_cristo_religious_province'):
            if res.rel_province_id != self.env.user.rel_province_id:
                raise UserError(_("Sorry! You cannot create other province Institution."))
        return res
    
    def write(self, vals):
        province_id = vals.get('rel_province_id', False) or self.rel_province_id.id
        if self.user_has_groups('cristo.group_role_cristo_religious_province'):
            if province_id != self.env.user.rel_province_id.id:
                raise UserError(_("Sorry! You cannot create other province Institution."))
        return super(Institution, self).write(vals)
    
    def unlink(self):
        contacts = self.mapped('partner_id')
        super(Institution, self).unlink()
        return contacts.unlink()
    
class MemberMinistry(models.Model):
    _name = 'res.member.ministry'
    _description = 'Ministry Details'
    
    @api.depends('member_id')
    def _compute_email_mobile(self):
        for member in self:
            if member:
                member.email = member.member_id.partner_id.email
                member.mobile = member.member_id.partner_id.mobile
            
    @api.constrains('date_from','date_to')
    def date_validation(self):
        if self.date_from and self.date_to:
            cris_tools.date_validation(self.date_from, self.date_to)     
    
    member_id = fields.Many2one('res.member', string="Member", ondelete="restrict", required=True)
    role_id = fields.Many2one('res.member.role', string="Role", ondelete="restrict")
    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")
    email = fields.Char(string="Email", compute='_compute_email_mobile')
    mobile = fields.Char(string="Mobile", compute='_compute_email_mobile')
    institute_id = fields.Many2one('res.religious.institute', string="Congregation", ondelete="restrict")   
    community_id = fields.Many2one('res.community', string="House/Community", ondelete="restrict")
    rel_region_id = fields.Many2one('res.religious.region', string="Religious Region", ondelete="restrict")
    institution_id = fields.Many2one('res.institution', string="Institution", ondelete="restrict")
    rel_province_id = fields.Many2one('res.religious.province', string="Religious Province", ondelete="restrict")
    main_category_id = fields.Many2one('res.main.category', string='Main Category')
    ecc_reg_id = fields.Many2one('res.ecclesia.region',string="Region", ondelete="restrict")
    ecc_province_id = fields.Many2one('res.ecclesia.province', string="Province", ondelete="restrict")
    diocese_id = fields.Many2one('res.ecclesia.diocese', ondelete="restrict", string="Diocese")
    vicariate_id = fields.Many2one('res.vicariate', ondelete="restrict", string="Vicariate")
    parish_id = fields.Many2one('res.parish', ondelete="restrict", string="Parish/Mission Station")
    status = fields.Selection([('active','Active'),('complete','Complete')], string="Status")
    type = fields.Selection([('council','Council'),('commission','Commission')], string="Type")
   
class Association(models.Model):
    _name = 'res.association'
    _description = "Association"
    _inherits = {'res.partner':'partner_id'}
    _inherit = ['address.loading','mail.thread','partner.clear.cache']
    _custom_filter_exclude_fields = Common_Excluded_Fields

    @api.model
    def default_get(self, fields):
        data = super(Association, self).default_get(fields)
        main_category = self.env['res.main.category'].search([('code', '=', 'AS')], limit=1)
        data['main_category_id'] = main_category.id or []
        data['company_type'] = 'company'
        return data
    
    partner_id = fields.Many2one('res.partner', string="Contact", ondelete="cascade", required=True)
    establishment_date = fields.Date(string="Establishment Date")
    institute_id = fields.Many2one('res.religious.institute', string="Congregation", ondelete="restrict")   
    rel_province_id = fields.Many2one('res.religious.province', string="Religious Province", ondelete="restrict")
    
class LegalEntity(models.Model):
    _name = 'res.legal.entity'
    _description = "Legal Entity"
    _inherits = {'res.partner':'partner_id'}
    _inherit = ['address.loading','mail.thread','partner.clear.cache','attachment.size']
    _custom_filter_exclude_fields = Common_Excluded_Fields

    @api.model
    def default_get(self, fields):
        data = super(LegalEntity, self).default_get(fields)
        main_category = self.env['res.main.category'].search([('code', '=', 'LE')], limit=1)
        data['main_category_id'] = main_category.id or []
        data['company_type'] = 'company'
        return data
    
    partner_id = fields.Many2one('res.partner', string="Contact", ondelete="cascade", required=True)
    diocese_id = fields.Many2one('res.ecclesia.diocese', string="Diocese", ondelete="restrict", tracking=True)
    rel_province_id = fields.Many2one('res.religious.province', string="Province", ondelete="restrict", tracking=True)
    category_type_id = fields.Many2one('res.institution.category', string="Institution Type", ondelete="restrict")
    establishment_date = fields.Date(string="Establishment Date")
    house_id = fields.Many2one('res.community', string="House/Community", tracking=True)
    entity_type = fields.Selection([
                        ('society','Society'),
                        ('trust','Trust'),
                        ('company_pvt',"Company(Pvt Ltd.)"),
                        ('company_non_profit',"Company(Non-Profitable)")
                                ],string="Type", required=True)
    incharge_id = fields.Many2one('res.partner', string="In-Charge", required=True)
    registration_no = fields.Char(string="Registration No.")
    renewal_date = fields.Date(string="Renewal Date")
    ngo_darpan_no = fields.Char(string="NGO Darpan No.")
    company_no = fields.Char(string="Company No.")
    nature_ids = fields.Many2many('entity.nature', string="Nature")
    founding_fathers = fields.Text(string="Founding Fathers")
    office_bearers_ids = fields.One2many('entity.office.bearer','entity_id', string="Office Bearers")
    document_ids = fields.One2many('entity.document','entity_id', string="Documents")
    bank_ids = fields.One2many('res.partner.bank','entity_id', string="Bank Details")
    audit_ids = fields.One2many('entity.audit','entity_id', string="Audit Details")
    fcra_no = fields.Char(string="FCRA No.")
    annual_return = fields.Selection([
                                ('done','Done'),
                                ('not_done', 'Not Done')
                                    ],string="Annual Return")
    attention = fields.Text(string="Matters Needing Urgent Attention")
    attachment_ids = fields.Many2many("ir.attachment", string="Documents")
    help_person_name = fields.Char(string="Person Name")
    help_person_phone = fields.Char(string="Person Phone")

class EntityOfficeBearer(models.Model):
    _name = "entity.office.bearer"
    _description = "Entity Office Bearer"

    entity_id = fields.Many2one("res.legal.entity", string="Legal Entity", ondelete="cascade")
    partner_id = fields.Many2one("res.partner", string="Member", required=True)
    role_id = fields.Many2one("res.member.role", string="Role", required=True)
    date_from = fields.Date(string="Date From")
    date_to = fields.Date(string="Date To")
    status = fields.Selection([
                    ('active','Active'),
                    ('archive', 'Archive')
                            ],string="Status", required=True)

class EntityDocuments(models.Model):
    _name = "entity.document"
    _description = "Entity Documents"

    name = fields.Char(string="Name", required=True)
    number = fields.Char(string="Number")
    document = fields.Binary(string="Document")
    entity_id = fields.Many2one("res.legal.entity", string="Legal Entity", ondelete="cascade")

class ResPartnerBank(models.Model):
    _inherit = "res.partner.bank"
    _description = "Bank Accounts"

    entity_id = fields.Many2one("res.legal.entity", string="Legal Entity", ondelete="cascade")

class EntityAudit(models.Model):
    _name = "entity.audit"
    _description = "Entity Audit"

    name = fields.Char(string="Auditor Name", required=True)
    fiscal_year_id = fields.Many2one("fiscal.year", string="Fiscal Year", required=True)
    statement = fields.Selection([
                            ('audited','Audited'),
                            ('not_audited', 'Not Audited')
                                ], string="Statement", required=True)
    entity_id = fields.Many2one("res.legal.entity", string="Legal Entity", ondelete="cascade")

class HouseMembers(models.Model):
    _name = 'house.member'
    _description = "Member Ministry"
    _rec_name = 'member_id'
    _order = 'date_from desc'
    
    member_id = fields.Many2one('res.member', string="Member", required=True, ondelete="cascade")
#     membership_member_ids = fields.Many2many('res.member',compute="_compute_membership_list")
    house_id = fields.Many2one('res.community', string="House ID")
    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")
    member_role_ids = fields.One2many('house.member.role', 'house_member_id', string="House Member Role")
    role_ids = fields.Many2many('res.member.role',string="Roles",compute="_compute_member_roles")
    status = fields.Selection([('active','Active'),('completed','Completed')], string="Status", required=True)
    
#     @api.depends('member_role_ids')
#     def _compute_membership_list(self):
#         self.membership_member_ids = self.env['res.membership'].search([('status','!=','exit')]).mapped('member_id')
    
    @api.depends('member_role_ids')
    def _compute_member_roles(self):
        for hm in self:
            if hm.member_role_ids:
                hm.role_ids = hm.member_role_ids.mapped('role_ids')
            else:
                hm.role_ids = []
    
    @api.constrains('date_from','date_to')
    def date_validation(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                cris_tools.date_validation(rec.date_from, rec.date_to)

    @api.constrains('member_id', 'house_id', 'status')
    def active_status_validation(self):
        for rec in self:
            if rec.status == 'active':
                member_ids = self.env['house.member'].search([('member_id','=', rec.member_id.id),('id','!=', rec.id)])
                for member in member_ids:
                    if member.status == 'active':
                        raise ValidationError(_("%s is already active in %s house.You cannot create another active Work House") % (member.member_id.member_name, member.house_id.name))

    @api.constrains('status')
    def date_to_value_confirmation(self):
        for rec in self:
            if rec.status == 'completed':
                if not rec.date_to:
                    raise UserError(_("Sorry! You need to enter the To Date to Complete the Ministry."))

    def _schedule_date_to(self):
        members = self.env['res.member'].search([])
        house_members = self.env['house.member']
        for m in members:
            house_member_id = self.env['house.member'].search([('member_id','=', m.id),('date_to', '=', False)],limit=1)
            house_member_ids = self.env['house.member'].search([('member_id', '=', m.id),('date_from','>', house_member_id.date_from)])
            if house_member_ids:
                member_ids = house_member_id+house_member_ids
                house_members = house_members + member_ids
        template_id = self.env.ref('cristo.email_template_house_member_date',raise_if_not_found=False)
        if template_id:
            try:
                template_id.with_context(house_members=house_members).send_mail(self.id,force_send=False, raise_exception=True)
            except MailDeliveryException:
                raise MailDeliveryException(_("Mail Delivery Failed"), '')

    @api.constrains('date_from')
    def from_date_validation(self):
        for rec in self:
            if rec.member_id and rec.member_id.dob:
                if rec.date_from.year <= (rec.member_id.dob.year + 20):
                    raise ValidationError("House/Ministry From Date Year Should be Greater than Member's DOB Year + 20")

    @api.constrains('date_from', 'date_to', 'member_role_ids')
    def date_from_validation(self):
        for rec in self:
            if rec.date_from:
                for role in rec.member_role_ids:
                    if role.date_from:
                        if not rec.date_from <= role.date_from:
                            raise UserError(_("House Member Role date from should between the Work House Dates."))
                    if role.date_to:
                        if not rec.date_from <= role.date_to:
                            raise UserError(_("House Member Role date to should between the Work House Dates."))
            if rec.date_to:
                for role in rec.member_role_ids:
                    if role.date_from:
                        if not rec.date_to >= role.date_from:
                            raise UserError(_("House Member Role date from should between the Work House Dates."))
                    if role.date_to:
                        if not rec.date_to >= role.date_to:
                            raise UserError(_("House Member Role date to should between the Work House Dates."))
    
    @api.model
    def create(self,vals):
        rec = super(HouseMembers, self).create(vals)
        if rec.status == 'active':
           rec.member_id.community_id = rec.house_id.id
        else:
            rec.member_id.community_id = False
        return rec
    
    def write(self, vals):
        rec = super(HouseMembers, self).write(vals)
        if self.status == 'active':
            self.member_id.community_id = self.house_id.id
        else:
            self.member_id.community_id = False
        return rec

class HouseMemberRole(models.Model):
    _name = 'house.member.role'
    _description = "House Member Role"
    
    member_id = fields.Many2one('res.member', string="Member", related="house_member_id.member_id")
    house_member_id = fields.Many2one('house.member', string="Member",ondelete='cascade')
    role_ids = fields.Many2many('res.member.role', string="Roles")
    institution_id = fields.Many2one('res.institution', string="Institution")
    house_id = fields.Many2one('res.community', string="House/Community")
    date_from = fields.Date(string="From")
    date_to = fields.Date(string="To")
    status = fields.Selection([('active','Active'),('completed','Completed')], compute="_compute_institution_member_status",string="Status",store=True)
   
    @api.constrains('date_from','date_to')
    def date_validation(self):
        for rec in self:
            if rec.date_from and rec.date_to:
                cris_tools.date_validation(rec.date_from, rec.date_to)
    
    @api.depends('house_member_id.status')
    def _compute_institution_member_status(self):
        for rec in self:
            rec.status = False
            rec.status = rec.house_member_id.status
    
class ResImportantDate(models.Model):
    _name = 'res.important.date'
    _description = "Important Date"

    name = fields.Char(string="Name", required=True)
    day = fields.Selection(DAYS, string="Day")
    month = fields.Selection(MONTHS, string="Month")
    institute_id = fields.Many2one('res.religious.institute', string="")
    rel_province_id = fields.Many2one('res.religious.province', string="Province")
    community_id = fields.Many2one('res.community', string="House/Community")
    institution_id = fields.Many2one('res.institution', string="Institution")
    type = fields.Selection([('feast_date','Feast Date'),('important_date','Important Date')], string="Type")

class ResRenewals(models.Model):
    _name = 'res.renewals'
    _description = "Org Renewals"
    _rec_name = 'document_type_id'

    no = fields.Char(string="Number")
    document = fields.Char(string="Document Name")
    document_type_id = fields.Many2one('renewal.doc.type', string="Document Type")
    agency = fields.Char(string="Agency")
    valid_from = fields.Date(string="Valid From")
    valid_to = fields.Date(string="Valid To")
    next_renewal = fields.Date(string="Next Renewal Date")
    rel_province_id = fields.Many2one('res.religious.province', string="Province")
    community_id = fields.Many2one('res.community', string="House/Community")
    institution_id = fields.Many2one('res.institution', string="Institution")
    proof = fields.Binary(string="Proof")
    store_name = fields.Char(string="File Name")
    
    @api.constrains('valid_from','valid_to')
    def date_validation(self):
        for rec in self:
            if rec.valid_from and rec.valid_to:
                if rec.valid_to < rec.valid_from:
                    raise UserError(_("Valid from date should not be lesser than the Valid Start date."))
    
    def org_renewal_notification_send(self):
        mail_server_id = self.env['ir.mail_server'].search([], limit=1)
        if mail_server_id:
            email_from = mail_server_id.smtp_user
            notificatiton_date = date.today() + timedelta(days=30)
            province_ids = self.env['res.religious.province'].search([])
            community_ids = self.env['res.community'].search([])
            institution_ids = self.env['res.institution'].search([])
            for province_id in province_ids:
                renewals_ids = self.env['res.renewals'].search([('rel_province_id', '=', province_id.id),('valid_to','=',notificatiton_date)])
                if renewals_ids:
                    email_to = province_id.email
                    name = province_id.full_name
                    if email_to:
                        template_id = self.env.ref('cristo.email_template_org_renewal_notification', raise_if_not_found=False)
                        if template_id:
                            try:
                                template_id.with_context(email_from=email_from,email_to=email_to,name=name,renewals_ids=renewals_ids).send_mail(renewals_ids[0].id, raise_exception=True)
                            except MailDeliveryException:
                                raise MailDeliveryException(_("Mail Delivery Failed"), '')
            for community_id in community_ids:
                renewals_ids = self.env['res.renewals'].search([('community_id', '=', community_id.id),('valid_to','=',notificatiton_date)])
                if renewals_ids:
                    email_to = community_id.email
                    name = community_id.full_name
                    if email_to:
                        template_id = self.env.ref('cristo.email_template_org_renewal_notification', raise_if_not_found=False)
                        if template_id:
                            try:
                                template_id.with_context(email_from=email_from,email_to=email_to,name=name,renewals_ids=renewals_ids).send_mail(renewals_ids[0].id, raise_exception=True)
                            except MailDeliveryException:
                                raise MailDeliveryException(_("Mail Delivery Failed"), '')
            for institution_id in institution_ids:
                renewals_ids = self.env['res.renewals'].search([('institution_id', '=', institution_id.id),('valid_to','=',notificatiton_date)])        
                if renewals_ids:
                    email_to = institution_id.email
                    name = institution_id.full_name
                    if email_to:
                        template_id = self.env.ref('cristo.email_template_org_renewal_notification', raise_if_not_found=False)
                        if template_id:
                            try:
                                template_id.with_context(email_from=email_from,email_to=email_to,name=name,renewals_ids=renewals_ids).send_mail(renewals_ids[0].id, raise_exception=True)
                            except MailDeliveryException:
                                raise MailDeliveryException(_("Mail Delivery Failed"), '')
                        
class HigherLevelProvincePeople(models.Model):
    _name = 'higher.level.rel_province.people'
    _description = "Higher Level Religious Province People"
   
    name = fields.Char(string="Name", required=True)
    role_id = fields.Many2one('res.member.role', string="Role")
    phone = fields.Char(string="Phone")
    email = fields.Char(string="Email")
    birth_day = fields.Selection(DAYS,string="Birth Day")
    birth_month = fields.Selection(MONTHS,string="Birth Month")
    feast_day = fields.Selection(DAYS,string="Feast Day")
    feast_month = fields.Selection(MONTHS,string="Feast Month")
    rel_province_id = fields.Many2one('res.religious.province', string="Province", ondelete="cascade") 
    
class RelProvinceStatistics(models.Model): 
    _name = 'rel.province.statistics'  
    _description = "Religious Province Statistics"
    
    type = fields.Char(string='Type')
    count = fields.Integer(string="Count")
    rel_province_id = fields.Many2one('res.religious.province', string="Province", ondelete="cascade")
    rel_pro_institution_id = fields.Many2one('res.religious.province', string="Province", ondelete="cascade")
    
                